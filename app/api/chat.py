"""Chat and query endpoints for DocuAssist API."""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.models import QueryRequest, QueryResponse
from app.rag.pipeline import RAGPipeline
from app.utils.logger import logger

router = APIRouter(prefix="/api/chat", tags=["chat"])


# Dependency for RAG pipeline
def get_rag_pipeline() -> RAGPipeline:
    """Dependency injection for RAG pipeline."""
    return RAGPipeline()


@router.post("/query", response_model=QueryResponse)
async def query_assistant(
    request: QueryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
) -> QueryResponse:
    """
    Process user query through RAG pipeline.

    - **query**: User's question (1-1000 characters)
    - **user_id**: Optional user identifier for tracking
    - **system_prompt**: Optional custom system behavior

    Returns structured response with generated answer, retrieved documents, and metrics.
    """
    try:
        # Input validation
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        query = request.query.strip()
        
        if len(query) > 1000:
            raise HTTPException(status_code=400, detail="Query is too long (max 1000 characters)")
        
        if len(query) < 1:
            raise HTTPException(status_code=400, detail="Query is too short (min 1 character)")

        # Process query
        result = pipeline.process_query(
            query=query,
            user_id=request.user_id or "anonymous",
            system_prompt=request.system_prompt
        )

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error occurred")
            logger.error(f"Query processing failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {error_msg}")

        return QueryResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in query endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/history/{user_id}")
async def get_conversation_history(
    user_id: str,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Retrieve conversation history for a user.

    Returns last 10 conversation exchanges for context in multi-turn conversations.
    """
    try:
        if not user_id or len(user_id) > 100:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        history = pipeline.get_conversation_history(user_id)
        return {
            "user_id": user_id,
            "message_count": len(history),
            "messages": history
        }
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation history")


@router.get("/health")
async def check_chat_health(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """
    Check RAG pipeline health status.

    Verifies vector store connectivity and LLM availability.
    """
    try:
        return pipeline.get_system_health()
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
