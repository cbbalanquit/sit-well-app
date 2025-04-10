from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class KeyPoint(BaseModel):
    """Model for a single keypoint with coordinates and confidence."""
    x: float
    y: float
    confidence: float

class PostureAnalysisRequest(BaseModel):
    """Model for posture analysis request with base64 image."""
    image: str = Field(..., description="Base64 encoded image data")

class PostureAnalysisResponse(BaseModel):
    """Model for posture analysis response with results and feedback."""
    isGoodPosture: bool = Field(..., description="Overall posture assessment")
    confidence: float = Field(..., description="Confidence score (0-100)")
    feedback: List[str] = Field(..., description="List of feedback messages")
    keypoints: Optional[Dict[str, KeyPoint]] = Field(None, description="Detected keypoints")
    img_with_pose: Optional[str] = Field(None, description="Base64 encoded image with pose overlay")

class HealthCheckResponse(BaseModel):
    """Model for health check response."""
    status: str
    message: str