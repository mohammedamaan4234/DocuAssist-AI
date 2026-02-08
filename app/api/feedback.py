"""Feedback and analytics endpoints for DocuAssist API."""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.models import FeedbackRequest, FeedbackResponse
from app.rag.pipeline import RAGPipeline
from app.utils.logger import logger

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


def get_rag_pipeline() -> RAGPipeline:
    """Dependency injection for RAG pipeline."""
    return RAGPipeline()


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
) -> FeedbackResponse:
    """
    Submit user feedback on response quality.

    Feedback is logged for post-deployment iteration and acts as weak supervision
    signal for prompt tuning and retrieval improvements.

    Ratings:
    - 1: Poor, inaccurate or unhelpful
    - 2: Below average
    - 3: Average, acceptable
    - 4: Good, helpful
    - 5: Excellent, highly relevant and accurate
    """
    try:
        # Input validation
        if not request.query_id or len(request.query_id) > 100:
            raise HTTPException(status_code=400, detail="Invalid query ID")
        
        if not request.user_id or len(request.user_id) > 100:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        if not isinstance(request.rating, int) or not (1 <= request.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be an integer between 1 and 5")
        
        if request.feedback_text and len(request.feedback_text) > 500:
            raise HTTPException(status_code=400, detail="Feedback text is too long (max 500 characters)")

        # Record feedback
        success = pipeline.collect_feedback(
            query_id=request.query_id,
            user_id=request.user_id,
            rating=request.rating,
            feedback=request.feedback_text
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to record feedback")

        return FeedbackResponse(
            success=True,
            message=f"Thank you! Your {request.rating}-star rating has been recorded."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while recording feedback")


@router.get("/metrics")
async def get_feedback_metrics(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """
    Get aggregate feedback metrics.

    Returns statistics on user satisfaction and response quality.
    """
    try:
        # This would connect to a metrics database in production
        return {
            "message": "Metrics aggregation coming in v1.1",
            "metrics": {
                "average_rating": "TBD",
                "feedback_count": "TBD",
                "improvement_areas": "TBD"
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")
