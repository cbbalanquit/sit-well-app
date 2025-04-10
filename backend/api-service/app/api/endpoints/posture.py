import base64
import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import Dict, Any

from app.models.posture import PostureAnalysisRequest, PostureAnalysisResponse
from app.services.inference_client import InferenceClient

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency to get inference client
def get_inference_client():
    return InferenceClient()

@router.post(
    "/analyze", 
    response_model=PostureAnalysisResponse,
    summary="Analyze posture from base64 image",
    description="Analyzes sitting posture from a base64-encoded image"
)
async def analyze_posture(
    request: PostureAnalysisRequest,
    inference_client: InferenceClient = Depends(get_inference_client)
) -> Dict[str, Any]:
    """Analyze posture from base64 image data."""
    try:
        # Send image to inference service
        result = await inference_client.analyze_image(request.image)
        
        # Return analysis results
        return {
            "isGoodPosture": result.get("isGoodPosture", False),
            "confidence": result.get("confidence", 0),
            "feedback": result.get("feedback", ["Unable to analyze posture"]),
            "keypoints": result.get("keypoints"),
            "img_with_pose": result.get("img_with_pose")
        }
    except Exception as e:
        logger.error(f"Error analyzing posture: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing posture: {str(e)}"
        )

@router.post(
    "/analyze/upload", 
    response_model=PostureAnalysisResponse,
    summary="Analyze posture from uploaded image",
    description="Analyzes sitting posture from an uploaded image file"
)
async def analyze_uploaded_image(
    file: UploadFile = File(...),
    inference_client: InferenceClient = Depends(get_inference_client)
) -> Dict[str, Any]:
    """Analyze posture from an uploaded image file."""
    try:
        # Read uploaded file
        contents = await file.read()
        
        # Convert to base64
        base64_image = base64.b64encode(contents).decode("utf-8")
        
        # Send to inference service
        result = await inference_client.analyze_image(base64_image)
        
        # Return analysis results
        return {
            "isGoodPosture": result.get("isGoodPosture", False),
            "confidence": result.get("confidence", 0),
            "feedback": result.get("feedback", ["Unable to analyze posture"]),
            "keypoints": result.get("keypoints"),
            "img_with_pose": result.get("img_with_pose")
        }
    except Exception as e:
        logger.error(f"Error analyzing uploaded image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing uploaded image: {str(e)}"
        )
