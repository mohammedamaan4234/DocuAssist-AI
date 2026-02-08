"""Pinecone vector database integration for semantic retrieval."""

import time
from typing import List, Tuple
from pinecone import Pinecone
from openai import OpenAI
from app.config import settings
from app.utils.logger import logger

client = OpenAI(api_key=settings.openai_api_key)
pc = Pinecone(api_key=settings.pinecone_api_key)


class VectorStore:
    """Manages vector embeddings and semantic search using Pinecone."""

    def __init__(self):
        """Initialize Pinecone index connection."""
        try:
            self.index = pc.Index(settings.pinecone_index_name)
            self.embedding_model = settings.embedding_model
            logger.info(f"Connected to Pinecone index: {settings.pinecone_index_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone: {str(e)}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.

        Uses distributional semantics to encode semantic meaning in high-dimensional space.
        """
        try:
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise

    def add_documents(self, documents: List[dict]) -> int:
        """
        Index documents in vector store.

        Args:
            documents: List of dicts with 'id', 'text', and 'metadata' keys

        Returns:
            Number of successfully inserted vectors
        """
        try:
            vectors_to_upsert = []

            for doc in documents:
                embedding = self.get_embedding(doc['text'])
                vectors_to_upsert.append({
                    'id': doc['id'],
                    'values': embedding,
                    'metadata': {
                        'text': doc['text'],
                        'source': doc.get('metadata', {}).get('source', 'unknown'),
                        'timestamp': doc.get('metadata', {}).get('timestamp', ''),
                    }
                })

            # Batch upsert for efficiency
            self.index.upsert(vectors=vectors_to_upsert)
            logger.info(f"Successfully indexed {len(documents)} documents")
            return len(documents)
        except Exception as e:
            logger.error(f"Document indexing failed: {str(e)}")
            raise

    def retrieve(self, query: str, top_k: int = None) -> List[Tuple[str, float]]:
        """
        Retrieve most relevant documents using semantic similarity.

        Implements approximate nearest neighbor (ANN) search in vector space.

        Args:
            query: User query text
            top_k: Number of results to retrieve

        Returns:
            List of tuples (document_text, relevance_score)
        """
        if top_k is None:
            top_k = settings.top_k

        try:
            start_time = time.time()

            # Generate query embedding
            query_embedding = self.get_embedding(query)

            # Search for similar vectors
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract documents and scores
            retrieved_docs = [
                (match['metadata']['text'], match['score'])
                for match in results['matches']
            ]

            logger.info(f"Retrieved {len(retrieved_docs)} documents in {latency_ms:.2f}ms")
            return retrieved_docs

        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}", exc_info=True)
            return []

    def delete_documents(self, doc_ids: List[str]) -> bool:
        """Delete documents from vector store."""
        try:
            self.index.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents")
            return True
        except Exception as e:
            logger.error(f"Document deletion failed: {str(e)}")
            return False

    def health_check(self) -> dict:
        """Check vector store health and statistics."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "status": "healthy",
                "total_vectors": stats.total_vector_count,
                "index_name": settings.pinecone_index_name
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
