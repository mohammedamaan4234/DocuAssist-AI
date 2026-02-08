"""Integration tests for RAG pipeline."""

import pytest
from app.rag.pipeline import RAGPipeline
from unittest.mock import MagicMock, patch


class TestRAGPipeline:
    """Test RAG pipeline integration."""

    @pytest.fixture
    def pipeline(self):
        """Create RAG pipeline instance."""
        return RAGPipeline()

    @patch("app.rag.vector_store.VectorStore.retrieve")
    @patch("app.rag.generation.GenerationEngine.generate_response")
    def test_process_query(self, mock_generate, mock_retrieve, pipeline):
        """Test end-to-end query processing."""
        # Setup mocks
        mock_retrieve.return_value = [
            ("Document 1 content", 0.95),
            ("Document 2 content", 0.87)
        ]
        mock_generate.return_value = "Generated response based on context"

        # Process query
        result = pipeline.process_query("Test query", user_id="test_user")

        # Assertions
        assert result["success"] is True
        assert result["response"] == "Generated response based on context"
        assert len(result["retrieved_documents"]) == 2
        assert "metrics" in result
        assert result["metrics"]["document_count"] == 2

    def test_conversation_history(self, pipeline):
        """Test conversation history tracking."""
        # Add queries
        pipeline.conversation_history["user_1"] = [
            {"query": "Q1", "response": "A1", "timestamp": 123},
            {"query": "Q2", "response": "A2", "timestamp": 124}
        ]

        # Retrieve history
        history = pipeline.get_conversation_history("user_1")
        assert len(history) == 2

    @patch("app.rag.vector_store.VectorStore.health_check")
    def test_system_health(self, mock_health, pipeline):
        """Test system health check."""
        mock_health.return_value = {"status": "healthy", "total_vectors": 1000}

        health = pipeline.get_system_health()
        assert health["status"] == "healthy"

    def test_feedback_collection(self, pipeline):
        """Test feedback recording."""
        result = pipeline.collect_feedback(
            "query_1",
            "user_1",
            5,
            "Great answer!"
        )
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
