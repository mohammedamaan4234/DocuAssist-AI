"""LLM integration for conditional generation based on retrieved context."""

import time
from typing import Optional
from openai import OpenAI
from app.config import settings
from app.utils.logger import logger


class GenerationEngine:
    """Generates responses conditioned on retrieved documents using LLMs."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def generate_response(
        self,
        query: str,
        context_documents: list,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate grounded response using retrieved documents.

        Implements conditional generation where the LLM's output probability
        is conditioned on retrieved documents as context.

        Args:
            query: Original user query
            context_documents: Retrieved relevant documents
            system_prompt: Custom system prompt for role definition

        Returns:
            Generated response text
        """
        if not system_prompt:
            system_prompt = self._get_default_system_prompt()

        # Build context from retrieved documents
        context = self._build_context(context_documents)

        # Construct messages for LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]

        try:
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                top_p=0.95
            )

            answer = response.choices[0].message.content
            latency_ms = (time.time() - start_time) * 1000

            logger.info(f"Generated response in {latency_ms:.2f}ms ({len(answer)} chars)")

            return answer

        except Exception as e:
            logger.error(f"Generation failed: {str(e)}", exc_info=True)
            return "I apologize, but I encountered an error while generating a response. Please try again."

    def _get_default_system_prompt(self) -> str:
        """Return default system prompt for customer support."""
        return """You are DocuAssist, an AI customer support assistant for a software company.
Your role is to provide accurate, helpful responses based on company documentation.

Guidelines:
1. Answer questions based ONLY on the provided context/documentation
2. If the context doesn't contain the answer, clearly state this
3. Be concise and professional
4. Provide actionable solutions when possible
5. Avoid hallucinating information not in the documentation
6. If you're unsure, acknowledge uncertainty rather than guessing"""

    def _build_context(self, documents: list) -> str:
        """Build formatted context string from retrieved documents."""
        if not documents:
            return "No relevant documentation found."

        context_parts = []
        for i, (doc_text, score) in enumerate(documents, 1):
            # Format each document with relevance indicator
            relevance = "High" if score > 0.8 else "Medium" if score > 0.6 else "Low"
            context_parts.append(f"[Document {i}] (Relevance: {relevance})\n{doc_text}")

        return "\n\n".join(context_parts)

    def evaluate_response_quality(
        self,
        query: str,
        response: str,
        context_documents: list
    ) -> dict:
        """
        Evaluate response quality and identify hallucinations.

        Uses LLM to check if response is grounded in provided context.
        """
        evaluation_prompt = f"""Evaluate this response for accuracy and hallucination:
Query: {query}
Response: {response}
Context: {[doc[0][:200] for doc in context_documents]}

Rate (1-5) and identify any unsupported claims."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.2,
                max_tokens=200
            )
            return {"evaluation": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Response evaluation failed: {str(e)}")
            return {"evaluation": "Unknown", "error": str(e)}
