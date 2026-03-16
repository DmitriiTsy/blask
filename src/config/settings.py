"""Application settings and configuration."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Providers
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    # Search APIs
    serpapi_key: Optional[str] = Field(default=None, alias="SERPAPI_KEY")
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    google_cse_id: Optional[str] = Field(default=None, alias="GOOGLE_CSE_ID")

    # LangSmith (optional)
    langsmith_api_key: Optional[str] = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: Optional[str] = Field(default=None, alias="LANGSMITH_PROJECT")

    # Knowledge Base storage settings
    knowledge_base_storage: str = Field(default="local", alias="KNOWLEDGE_BASE_STORAGE")  # local, s3, gcs
    knowledge_base_path: Optional[str] = Field(default=None, alias="KNOWLEDGE_BASE_PATH")
    
    # Cloud storage (optional)
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    s3_bucket: Optional[str] = Field(default=None, alias="S3_BUCKET")
    gcs_bucket: Optional[str] = Field(default=None, alias="GCS_BUCKET")

    # Application settings
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # LLM Model settings
    default_model: str = Field(default="gpt-4o-mini")
    default_temperature: float = Field(default=0.7)

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern)."""
    return Settings()
