import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.models.inference import InferenceRequest, InferenceResponse
from app.services.pose_detector import get_pose_detector, PoseDetector
from app.services.posture_analyzer import analyze_posture
from app.core.errors import NoPersonDetectedError, ImageProcessingError

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/analyze", 
    response_model=InferenceResponse,
    summary="Analyze posture from image",
    description="Run inference on an image to detect pose and analyze posture"
)
async def analyze_image(
    request: InferenceRequest,
    pose_detector: PoseDetector = Depends(get_pose_detector)
) -> Dict[str, Any]:
    """Process image for pose detection and posture analysis."""
    try:
        # Run pose detection
        result = pose_detector.detect_pose(request.image)
        
        if not result or "keypoints" not in result:
            logger.warning("No pose detected in the image")
            raise NoPersonDetectedError()
        
        # Run posture analysis
        analysis_results = analyze_posture(result["keypoints"])
        
        # Construct response
        return {
            "isGoodPosture": analysis_results["is_good_posture"],
            "confidence": int(analysis_results["overall_score"] * 100),
            "feedback": analysis_results["feedback"],
            "keypoints": result["keypoints"],
            "img_with_pose": result["img_with_pose"],
            "analysis": {
                "shoulder_balance": analysis_results["shoulder_balance"],
                "neck_position": analysis_results["neck_position"],
                "back_position": analysis_results["back_position"],
                "overall_score": analysis_results["overall_score"],
                "is_good_posture": analysis_results["is_good_posture"]
            }
        }
    except NoPersonDetectedError as e:
        # This exception is already properly handled by the exception handler
        raise
    except ImageProcessingError as e:
        # This exception is already properly handled by the exception handler
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing image: {str(e)}"
        )