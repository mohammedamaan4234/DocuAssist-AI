"""Document management endpoints for DocuAssist API."""

from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from typing import List
from app.schemas.models import DocumentUploadRequest, UploadResponse
from app.rag.pipeline import RAGPipeline
import uuid

router = APIRouter(prefix="/api/documents", tags=["documents"])


def get_rag_pipeline() -> RAGPipeline:
    """Dependency injection for RAG pipeline."""
    return RAGPipeline()


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(
    request: DocumentUploadRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
) -> UploadResponse:
    """
    Upload and index documents for RAG system.

    Documents are converted to embeddings and stored in vector database for semantic search.

    Expected format:
    ```json
    {
        "documents": [
            {
                "id": "doc_1",
                "text": "Document content...",
                "metadata": {
                    "source": "help_docs",
                    "category": "account"
                }
            }
        ]
    }
    ```
    """
    if not request.documents:
        raise HTTPException(status_code=400, detail="No documents provided")

    try:
        # Validate and prepare documents
        documents_to_index = []
        for doc in request.documents:
            if 'text' not in doc or not doc['text'].strip():
                raise HTTPException(status_code=400, detail="Each document must have non-empty 'text' field")

            # Assign ID if not provided
            doc_id = doc.get('id', f"doc_{uuid.uuid4()}")
            documents_to_index.append({
                'id': doc_id,
                'text': doc['text'],
                'metadata': doc.get('metadata', {})
            })

        # Index documents in vector store
        count = pipeline.vector_store.add_documents(documents_to_index)

        return UploadResponse(
            success=True,
            documents_indexed=count,
            message=f"Successfully indexed {count} documents"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document indexing failed: {str(e)}")


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Delete a document from the vector store."""
    try:
        success = pipeline.vector_store.delete_documents([doc_id])
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete document")
        return {"success": True, "message": f"Document {doc_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_document_store_health(
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Check document store (vector database) health."""
    health = pipeline.vector_store.health_check()
    return health
