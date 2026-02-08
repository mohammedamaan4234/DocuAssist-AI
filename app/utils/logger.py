"""Logging configuration for DocuAssist AI."""

import logging
from datetime import datetime
from pathlib import Path
from app.config import settings

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_file = logs_dir / f"docuassist_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=log_format,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("docuassist")


class QueryLogger:
    """Logs queries and responses for monitoring and debugging."""

    @staticmethod
    def log_query(user_id: str, query: str, metadata: dict = None):
        """Log incoming query."""
        if settings.log_queries:
            meta_str = f" | {metadata}" if metadata else ""
            logger.info(f"QUERY | USER: {user_id} | TEXT: {query}{meta_str}")

    @staticmethod
    def log_retrieval(query: str, results_count: int, latency_ms: float):
        """Log retrieval operation metrics."""
        logger.info(f"RETRIEVAL | QUERY: {query} | RESULTS: {results_count} | LATENCY: {latency_ms}ms")

    @staticmethod
    def log_generation(query: str, response: str, latency_ms: float):
        """Log generation operation metrics."""
        logger.info(f"GENERATION | LATENCY: {latency_ms}ms | TOKENS: {len(response.split())}")

    @staticmethod
    def log_feedback(user_id: str, query_id: str, rating: int, feedback: str = None):
        """Log user feedback for post-deployment iteration."""
        logger.info(f"FEEDBACK | USER: {user_id} | QUERY_ID: {query_id} | RATING: {rating} | TEXT: {feedback}")

    @staticmethod
    def log_error(error_type: str, message: str, context: dict = None):
        """Log errors with context for debugging."""
        ctx_str = f" | CONTEXT: {context}" if context else ""
        logger.error(f"ERROR | TYPE: {error_type} | MSG: {message}{ctx_str}")
