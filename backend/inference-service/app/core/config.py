import os
from typing import List

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Inference Service Settings
    PROJECT_NAME: str = "SIT-WELL-APP Inference"
    PROJECT_DESCRIPTION: str = "Inference service for posture analysis"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]  # Should be restricted in production
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Model Settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "yolo11n-pose.pt")
    MODEL_CONFIDENCE: float = float(os.getenv("MODEL_CONFIDENCE", "0.5"))
    
    # Posture Analysis Settings
    SHOULDER_BALANCE_THRESHOLD: float = float(os.getenv("SHOULDER_BALANCE_THRESHOLD", "0.05"))
    NECK_TILT_THRESHOLD: float = float(os.getenv("NECK_TILT_THRESHOLD", "0.15"))
    BACK_ANGLE_THRESHOLD: float = float(os.getenv("BACK_ANGLE_THRESHOLD", "15.0"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings object
settings = Settings()