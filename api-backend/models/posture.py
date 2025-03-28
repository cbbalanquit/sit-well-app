from pydantic import BaseModel
from typing import List, Optional, Any

class PostureAnalysisResponse(BaseModel):
    status: str
    posture_quality: Optional[str] = None
    issues: List[str] = []
    recommendations: List[str] = []
    keypoints: List[Any] = []
