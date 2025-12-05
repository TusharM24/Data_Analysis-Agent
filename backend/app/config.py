"""Application configuration settings."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    app_name: str = "EDA Agent"
    debug: bool = True
    
    # Groq API
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
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
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

