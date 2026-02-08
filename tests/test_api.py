"""Unit tests for DocuAssist API."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from unittest.mock import patch, MagicMock

client = TestClient(app)


class TestHealthEndpoints:
    """Test system health monitoring."""

    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["name"] == settings.api_title
        assert response.json()["version"] == settings.api_version

    def test_health_check(self):
        """Test general health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestChatEndpoints:
    """Test chat query functionality."""

    @patch("app.rag.pipeline.RAGPipeline.process_query")
    def test_query_endpoint(self, mock_process):
        """Test query submission endpoint."""
        mock_process.return_value = {
            "query_id": "test-123",
            "response": "Test response",
            "retrieved_documents": [
                {"text": "Doc 1", "relevance_score": 0.95}
            ],
            "metrics": {
                "retrieval_latency_ms": 50,
                "generation_latency_ms": 1000,
                "total_latency_ms": 1050,
                "document_count": 1
            },
            "success": True
        }

        response = client.post(
            "/api/chat/query",
            json={"query": "How do I reset my password?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Test response"
        assert data["success"] is True

    def test_query_empty_validation(self):
        """Test that empty queries are rejected."""
        response = client.post(
            "/api/chat/query",
            json={"query": "   "}
        )
        assert response.status_code == 400

    @patch("app.rag.pipeline.RAGPipeline.get_conversation_history")
    def test_conversation_history(self, mock_history):
        """Test retrieving conversation history."""
        mock_history.return_value = [
            {
                "query_id": "test-1",
                "query": "Q1",
                "response": "A1",
                "timestamp": 123456789
            }
        ]

        response = client.get("/api/chat/history/user_123")
        assert response.status_code == 200
        assert len(response.json()["messages"]) == 1


class TestDocumentEndpoints:
    """Test document management."""

    @patch("app.rag.vector_store.VectorStore.add_documents")
    def test_document_upload(self, mock_add):
        """Test document upload endpoint."""
        mock_add.return_value = 1

        response = client.post(
            "/api/documents/upload",
            json={
                "documents": [
                    {
                        "id": "doc_1",
                        "text": "Documentation content",
                        "metadata": {"source": "help_docs"}
                    }
                ]
            }
        )

        assert response.status_code == 200
        assert response.json()["documents_indexed"] == 1

    def test_document_upload_no_documents(self):
        """Test upload fails with empty documents."""
        response = client.post(
            "/api/documents/upload",
            json={"documents": []}
        )
        assert response.status_code == 400

    def test_document_upload_missing_text(self):
        """Test upload fails when text field is missing."""
        response = client.post(
            "/api/documents/upload",
            json={
                "documents": [
                    {"id": "doc_1", "metadata": {}}
                ]
            }
        )
        assert response.status_code == 400


class TestFeedbackEndpoints:
    """Test feedback collection."""

    @patch("app.rag.pipeline.RAGPipeline.collect_feedback")
    def test_submit_feedback(self, mock_feedback):
        """Test feedback submission."""
        mock_feedback.return_value = True

        response = client.post(
            "/api/feedback/submit",
            json={
                "query_id": "test-123",
                "user_id": "user_1",
                "rating": 5,
                "feedback_text": "Great response!"
            }
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_feedback_invalid_rating(self):
        """Test feedback validation for rating range."""
        response = client.post(
            "/api/feedback/submit",
            json={
                "query_id": "test-123",
                "user_id": "user_1",
                "rating": 10  # Invalid
            }
        )
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
