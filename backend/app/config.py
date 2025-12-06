"""Application configuration settings."""
import os
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List


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
    
    # CORS - Parse from environment variable or use defaults
    cors_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="CORS_ORIGINS"
    )
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if not self.cors_origins_str:
            return []
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        populate_by_name = True  # Allow both field name and alias


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()


