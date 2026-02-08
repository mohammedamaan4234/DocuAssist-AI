"""Configuration management for DocuAssist AI."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "DocuAssist AI"
    api_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-3-small"

    # Pinecone Configuration
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "docuassist"

    # RAG Parameters
    max_retrieved_documents: int = 3
    top_k: int = 3
    temperature: float = 0.7
    max_tokens: int = 500

    # Monitoring & Logging
    enable_monitoring: bool = True
    log_queries: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
