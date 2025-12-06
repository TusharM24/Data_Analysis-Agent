"""Application configuration settings."""
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import List, Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    app_name: str = "EDA Agent"
    debug: bool = True
    
    # Groq API
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    
    # File Storage
    upload_dir: str = "./data/uploads"
    plots_dir: str = "./data/plots"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    # Code Execution
    execution_timeout: int = 30  # seconds
    max_rows_preview: int = 1000
    
    # Session Settings
    session_ttl: int = 3600 * 24  # 24 hours
    
    # CORS - Can be a comma-separated string or a list
    cors_origins: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173"
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        env_prefix = ""  # No prefix for environment variables


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()


