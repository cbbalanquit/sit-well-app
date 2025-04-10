import os
from typing import List

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Service Settings
    PROJECT_NAME: str = "SIT-WELL-APP API"
    PROJECT_DESCRIPTION: str = "API Service for posture analysis application"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]  # For development - should be restricted in production
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Inference Service Settings
    INFERENCE_SERVICE_URL: str = os.getenv("INFERENCE_SERVICE_URL", "http://inference_service:8001")
    INFERENCE_TIMEOUT: int = int(os.getenv("INFERENCE_TIMEOUT", "30"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings object
settings = Settings()
