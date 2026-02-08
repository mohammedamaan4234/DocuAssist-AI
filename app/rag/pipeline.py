"""RAG pipeline integrating retrieval and generation."""

import time
import uuid
from typing import Optional
from app.rag.vector_store import VectorStore
from app.rag.generation import GenerationEngine
from app.utils.logger import logger, QueryLogger


# Mock knowledge base for demo mode
MOCK_KNOWLEDGE_BASE = {
    "password": {
        "queries": ["reset password", "forgot password", "change password"],
        "response": "To reset your password:\n\n1. Go to the login page\n2. Click 'Forgot Password?' link\n3. Enter your email address\n4. Check your email for a reset link (valid for 24 hours)\n5. Click the link and create a new password (minimum 8 characters with uppercase, lowercase, and numbers)\n6. Sign in with your new password\n\nIf you don't receive the email within 5 minutes, check your spam folder or contact support@company.com",
        "docs": [{"text": "Password reset requires email verification. Reset links expire after 24 hours.", "relevance_score": 0.95}]
    },
    "billing": {
        "queries": ["pricing", "cost", "refund", "billing", "payment"],
        "response": "Pricing & Billing Information:\n\n📊 Plans:\n- Starter: $29/month (100 users)\n- Professional: $99/month (500 users)  \n- Enterprise: Custom pricing\n\n💳 Payment Methods:\nVisa, Mastercard, American Express, and bank transfers\n\n📅 Billing Benefits:\n- 20% discount on annual plans\n- 30-day money-back guarantee\n- Cancel anytime\n\nFor more details, visit your Billing page or contact support.",
        "docs": [{"text": "Annual billing plans receive 20% discount. All plans include 30-day money-back guarantee.", "relevance_score": 0.92}]
    },
    "support": {
        "queries": ["contact support", "customer support", "help", "support"],
        "response": "How to Contact Support:\n\n📧 Email: support@company.com (24 hours, business days)\n💬 Live Chat: Monday-Friday, 9 AM - 5 PM EST\n☎️ Phone: 1-800-COMPANY (Enterprise only, M-F 9 AM - 6 PM EST)\n📚 Help Center: help.company.com (instant answers, 24/7)\n🌍 Community: community.company.com (get help from other users)\n\nResponse Times:\n⚡ Critical issues: 1 hour\n🔴 High priority: 4 hours\n🟡 Medium priority: 24 hours\n🟢 Low priority: 48 hours",
        "docs": [{"text": "Support team available via email, live chat, and community forum. Enterprise customers have phone support.", "relevance_score": 0.94}]
    },
    "account": {
        "queries": ["create account", "sign up", "new account", "registration"],
        "response": "Creating a New Account:\n\n1. Visit our website and click 'Sign Up'\n2. Enter your email address\n3. Create a strong password (min 8 chars: uppercase, lowercase, number)\n4. Select your organization type\n5. Accept Terms of Service & Privacy Policy\n6. Click 'Create Account'\n7. Verify email via link (check spam folder if needed)\n8. Complete your profile\n\n🎁 Your account includes:\n✅ 30-day free trial with full features\n✅ Community support access\n✅ Basic analytics dashboard",
        "docs": [{"text": "New accounts get 30-day free trial access to all features with community support included.", "relevance_score": 0.96}]
    },
    "security": {
        "queries": ["security", "2fa", "two factor", "encryption", "data privacy"],
        "response": "Security & Privacy Features:\n\n🔐 Two-Factor Authentication (2FA):\n- Extra layer of protection\n- Use authenticator app (Google Authenticator, Authy) or SMS\n- Enable in Settings > Security\n\n🛡️ Data Protection:\n✅ All data encrypted in transit (HTTPS/TLS)\n✅ GDPR & CCPA compliant\n✅ SOC 2 Type II certified\n✅ You own your data and can export anytime\n\n🔑 Login Security:\n- Auto-logout after 5 minutes inactivity\n- Session management available\n- Unusual login alerts via email",
        "docs": [{"text": "All data is encrypted with TLS. 2FA available for extra security. GDPR and CCPA compliant.", "relevance_score": 0.93}]
    }
}


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.

    Combines semantic retrieval with LLM generation to provide
    accurate, grounded responses.
    """

    def __init__(self):
        """Initialize retrieval and generation components."""
        try:
            self.vector_store = VectorStore()
            self.generation_engine = GenerationEngine()
            self.demo_mode = False
        except Exception as e:
            logger.warning(f"Could not initialize vector store (using demo mode): {e}")
            self.vector_store = None
            self.generation_engine = None
            self.demo_mode = True
        
        self.conversation_history = {}

    def process_query(
        self,
        query: str,
        user_id: str = "anonymous",
        system_prompt: Optional[str] = None
    ) -> dict:
        """
        Process user query through RAG pipeline.

        Args:
            query: User's question
            user_id: Identifier for user feedback tracking
            system_prompt: Optional custom system prompt

        Returns:
            Dictionary with response, metadata, and metrics
        """
        query_id = str(uuid.uuid4())
        start_time = time.time()

        # Log incoming query
        QueryLogger.log_query(user_id, query, {"query_id": query_id})

        try:
            # Use demo mode if vector store unavailable
            if self.demo_mode:
                return self._process_query_demo_mode(query, query_id, user_id, start_time)
            
            # Phase 1: RETRIEVAL - Semantic search in vector space
            retrieval_start = time.time()
            retrieved_docs = self.vector_store.retrieve(query)
            retrieval_latency = (time.time() - retrieval_start) * 1000

            QueryLogger.log_retrieval(query, len(retrieved_docs), retrieval_latency)

            if not retrieved_docs:
                logger.warning(f"No relevant documents found for query: {query}")

            # Phase 2: GENERATION - LLM conditioned on context
            generation_start = time.time()
            response = self.generation_engine.generate_response(
                query,
                retrieved_docs,
                system_prompt
            )
            generation_latency = (time.time() - generation_start) * 1000

            QueryLogger.log_generation(query, response, generation_latency)

            total_latency = (time.time() - start_time) * 1000

            # Compile result with metadata
            result = {
                "query_id": query_id,
                "response": response,
                "retrieved_documents": [
                    {
                        "text": doc[0],
                        "relevance_score": doc[1]
                    }
                    for doc in retrieved_docs
                ],
                "metrics": {
                    "retrieval_latency_ms": retrieval_latency,
                    "generation_latency_ms": generation_latency,
                    "total_latency_ms": total_latency,
                    "document_count": len(retrieved_docs)
                },
                "success": True
            }

            # Store in conversation history for context
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            self.conversation_history[user_id].append({
                "query_id": query_id,
                "query": query,
                "response": response,
                "timestamp": time.time()
            })

            return result

        except Exception as e:
            logger.error(f"RAG pipeline error: {str(e)}", exc_info=True)
            QueryLogger.log_error("RAG_PIPELINE", str(e), {"query_id": query_id})
            return {
                "query_id": query_id,
                "response": "An error occurred processing your request. Please try again.",
                "success": False,
                "error": str(e)
            }

    def _process_query_demo_mode(self, query: str, query_id: str, user_id: str, start_time: float) -> dict:
        """
        Process query in demo mode (when vector store is unavailable).
        
        Uses pre-configured mock knowledge base for common support questions.
        """
        retrieval_start = time.time()
        query_lower = query.lower()
        
        # Find matching knowledge base entry
        response = None
        retrieved_docs = []
        
        for category, kb_entry in MOCK_KNOWLEDGE_BASE.items():
            if any(keyword in query_lower for keyword in kb_entry["queries"]):
                response = kb_entry["response"]
                retrieved_docs = kb_entry["docs"]
                break
        
        # Fallback response
        if not response:
            response = "I'm running in demo mode with limited knowledge. Here's what I can help with:\n\n📌 Password Reset\n💰 Pricing & Billing  \n📞 Contact Support\n📝 Account Creation\n🔒 Security Features\n\nPlease ask about any of these topics for detailed information!"
            retrieved_docs = [{"text": "Demo mode - Limited knowledge base", "relevance_score": 0.5}]
        
        retrieval_latency = (time.time() - retrieval_start) * 1000
        generation_latency = 150.0  # Simulated LLM latency
        total_latency = (time.time() - start_time) * 1000
        
        result = {
            "query_id": query_id,
            "response": response,
            "retrieved_documents": retrieved_docs,
            "metrics": {
                "retrieval_latency_ms": retrieval_latency,
                "generation_latency_ms": generation_latency,
                "total_latency_ms": total_latency,
                "document_count": len(retrieved_docs)
            },
            "success": True,
            "mode": "demo"  # Indicate demo mode
        }
        
        # Store in conversation history
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        self.conversation_history[user_id].append({
            "query_id": query_id,
            "query": query,
            "response": response,
            "timestamp": time.time()
        })
        
        return result

    def collect_feedback(self, query_id: str, user_id: str, rating: int, feedback: Optional[str] = None) -> bool:
        """
        Collect user feedback for iterative improvement.

        Feedback acts as weak supervision signal for prompt tuning and retrieval improvements.

        Args:
            query_id: ID of the original query
            user_id: User identifier
            rating: 1-5 rating of response quality
            feedback: Optional text feedback

        Returns:
            Success status
        """
        try:
            QueryLogger.log_feedback(user_id, query_id, rating, feedback)
            logger.info(f"Feedback recorded for query {query_id}: {rating}/5")
            return True
        except Exception as e:
            logger.error(f"Failed to collect feedback: {str(e)}")
            return False

    def get_conversation_history(self, user_id: str) -> list:
        """Retrieve conversation history for a user (last 10 exchanges)."""
        if user_id not in self.conversation_history:
            return []
        return self.conversation_history[user_id][-10:]

    def get_system_health(self) -> dict:
        """Check overall system health."""
        try:
            vector_store_health = self.vector_store.health_check()
            return {
                "status": "healthy",
                "components": {
                    "vector_store": vector_store_health
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
