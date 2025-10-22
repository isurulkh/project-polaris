"""
Project Polaris Configuration Settings
Production-ready configuration management with validation
"""

from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Project Polaris"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")
    
    # Google Gemini API
    google_api_key: str = Field(..., description="Google AI API Key")
    gemini_model_flash: str = Field(default="gemini-2.5-flash-latest", description="Fast model for queries")
    gemini_model_pro: str = Field(default="gemini-2.5-pro-latest", description="Advanced model for summaries")
    gemini_embedding_model: str = Field(default="models/text-embedding-004", description="Embedding model")
    gemini_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    gemini_max_output_tokens: int = Field(default=8192)
    gemini_top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    gemini_top_k: int = Field(default=40, ge=1)
    
    # Supabase Database (PGVector)
    database_url: str = Field(
        ...,
        description="Supabase PostgreSQL connection URL"
    )
    supabase_key: str = Field(
        ...,
        description="Supabase anon public key from Settings > API"
    )
    
    # Vector Store Configuration
    embedding_dimension: int = Field(default=768, description="Embedding vector dimension")
    collection_name: str = Field(default="google_drive_documents", description="Vector collection name")
    distance_metric: str = Field(default="cosine", description="Distance metric: cosine, l2, ip")
    
    # Supabase Specific (from n8n workflow)
    supabase_table_name: str = Field(default="documents_2", description="Supabase table name")
    supabase_query_name: str = Field(default="match_documents", description="Supabase query function name")
    
    # RAG Configuration
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    top_k_retrieval: int = Field(default=20, ge=1, le=100, description="Initial retrieval count")
    top_k_final: int = Field(default=5, ge=1, le=20, description="Final context documents")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Advanced RAG
    enable_hyde: bool = Field(default=True, description="Enable HyDE")
    enable_reranking: bool = Field(default=True, description="Enable cross-encoder reranking")
    enable_hybrid_search: bool = Field(default=True, description="Enable hybrid search")
    rerank_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    # Redis Cache
    redis_url: Optional[str] = Field(default="redis://localhost:6379/0", description="Redis URL")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    enable_cache: bool = Field(default=True, description="Enable caching")
    
    # Authentication
    secret_key: str = Field(..., description="JWT secret key")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60)
    rate_limit_burst: int = Field(default=10)
    
    # Monitoring
    enable_prometheus: bool = Field(default=True)
    prometheus_port: int = Field(default=9090)
    log_level: str = Field(default="INFO")
    
    # Conversation History
    max_conversation_history: int = Field(default=10, description="Max conversation turns to keep")
    conversation_store_enabled: bool = Field(default=True)
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("Database URL must start with postgresql:// or postgres://")
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"


# Global settings instance
settings = Settings()


# Database configuration helper
def get_database_config() -> dict:
    """Get database configuration dictionary"""
    return {
        "url": settings.database_url,
        "echo": settings.debug and settings.is_development,
        "pool_size": 20 if settings.is_production else 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }


# Gemini configuration helper
def get_gemini_config(model_type: str = "flash") -> dict:
    """Get Gemini model configuration"""
    model_name = (
        settings.gemini_model_pro 
        if model_type == "pro" 
        else settings.gemini_model_flash
    )
    
    return {
        "model": model_name,  # Changed from "model_name" to "model"
        "google_api_key": settings.google_api_key,
        "temperature": settings.gemini_temperature,
        "max_output_tokens": settings.gemini_max_output_tokens,
        "top_p": settings.gemini_top_p,
        "top_k": settings.gemini_top_k,
    }