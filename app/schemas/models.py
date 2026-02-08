"""Request and response data models for DocuAssist API."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============== Request Models ==============

class QueryRequest(BaseModel):
    """User query request."""

    query: str = Field(..., min_length=1, max_length=1000, description="User's question")
    user_id: str = Field(default="anonymous", description="User identifier for tracking")
    system_prompt: Optional[str] = Field(None, description="Optional custom system prompt")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I reset my password?",
                "user_id": "user_123"
            }
        }


class DocumentUploadRequest(BaseModel):
    """Request to upload documents for RAG indexing."""

    documents: List[dict] = Field(..., description="List of documents to index")

    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "id": "doc_1",
                        "text": "Password reset instructions...",
                        "metadata": {"source": "help_docs", "category": "account"}
                    }
                ]
            }
        }


class FeedbackRequest(BaseModel):
    """User feedback on response quality."""

    query_id: str = Field(..., description="ID of the original query")
    user_id: str = Field(..., description="User identifier")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback_text: Optional[str] = Field(None, max_length=500, description="Optional feedback text")

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "abc-123-def",
                "user_id": "user_123",
                "rating": 4,
                "feedback_text": "Response was helpful but could be more detailed"
            }
        }


# ============== Response Models ==============

class DocumentMetadata(BaseModel):
    """Metadata for a retrieved document."""

    text: str = Field(description="Document content")
    relevance_score: float = Field(description="Relevance score 0-1")


class MetricsData(BaseModel):
    """Performance metrics for a query."""

    retrieval_latency_ms: float = Field(description="Time to retrieve documents (ms)")
    generation_latency_ms: float = Field(description="Time to generate response (ms)")
    total_latency_ms: float = Field(description="Total query processing time (ms)")
    document_count: int = Field(description="Number of documents retrieved")


class QueryResponse(BaseModel):
    """Response to a user query."""

    query_id: str = Field(description="Unique query identifier for feedback")
    response: str = Field(description="Generated response text")
    retrieved_documents: List[DocumentMetadata] = Field(description="Retrieved source documents")
    metrics: MetricsData = Field(description="Performance metrics")
    success: bool = Field(description="Whether query was successfully processed")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "abc-123-def",
                "response": "To reset your password...",
                "retrieved_documents": [
                    {
                        "text": "Password reset instructions...",
                        "relevance_score": 0.95
                    }
                ],
                "metrics": {
                    "retrieval_latency_ms": 45.2,
                    "generation_latency_ms": 1250.5,
                    "total_latency_ms": 1295.7,
                    "document_count": 3
                },
                "success": True
            }
        }


class UploadResponse(BaseModel):
    """Response to document upload."""

    success: bool = Field(description="Whether upload was successful")
    documents_indexed: int = Field(description="Number of documents successfully indexed")
    message: str = Field(description="Status message")


class FeedbackResponse(BaseModel):
    """Response to feedback submission."""

    success: bool = Field(description="Whether feedback was recorded")
    message: str = Field(description="Status message")


class HealthResponse(BaseModel):
    """System health status."""

    status: str = Field(description="Overall system status (healthy/unhealthy)")
    components: Optional[dict] = Field(None, description="Status of individual components")
    error: Optional[str] = Field(None, description="Error message if unhealthy")


class ConversationMessage(BaseModel):
    """Single message in conversation history."""

    query: str = Field(description="User's question")
    response: str = Field(description="Assistant's response")
    timestamp: float = Field(description="Unix timestamp")


class ConversationHistoryResponse(BaseModel):
    """User's conversation history."""

    user_id: str = Field(description="User identifier")
    messages: List[ConversationMessage] = Field(description="Conversation messages")
