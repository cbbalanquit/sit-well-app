from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class KeyPoint(BaseModel):
    """Model for a single keypoint with coordinates and confidence."""
    x: float
    y: float
    confidence: float

class InferenceRequest(BaseModel):
    """Model for inference request with base64 image."""
    image: str = Field(..., description="Base64 encoded image data")

class PostureKeypoints(BaseModel):
    """Model for keypoints relevant to posture analysis."""
    left_ear: Optional[KeyPoint] = None
    right_ear: Optional[KeyPoint] = None
    left_shoulder: Optional[KeyPoint] = None
    right_shoulder: Optional[KeyPoint] = None
    left_hip: Optional[KeyPoint] = None
    right_hip: Optional[KeyPoint] = None

class PostureAnalysis(BaseModel):
    """Model for posture analysis results."""
    shoulder_balance: float = Field(..., description="Score for shoulder balance (0-1)")
    neck_position: float = Field(..., description="Score for neck position (0-1)")
    back_position: float = Field(..., description="Score for back position (0-1)")
    overall_score: float = Field(..., description="Overall posture score (0-1)")
    is_good_posture: bool = Field(..., description="Overall posture assessment")

class InferenceResponse(BaseModel):
    """Model for inference response with analysis results."""
    isGoodPosture: bool = Field(..., description="Overall posture assessment")
    confidence: float = Field(..., description="Confidence score (0-100)")
    feedback: List[str] = Field(..., description="List of feedback messages")
    keypoints: Optional[Dict[str, KeyPoint]] = Field(None, description="Detected keypoints")
    img_with_pose: Optional[str] = Field(None, description="Base64 encoded image with pose overlay")
    analysis: Optional[PostureAnalysis] = Field(None, description="Detailed posture analysis")