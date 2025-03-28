from fastapi import APIRouter, UploadFile, File, HTTPException
from services.inference import get_pose_keypoints
from services.posture_analyzer import analyze_posture
from models.posture import PostureAnalysisResponse

router = APIRouter(prefix="/posture", tags=["posture"])

@router.post("/analyze", response_model=PostureAnalysisResponse)
async def analyze_posture_image(file: UploadFile = File(...)):
    """
    Analyze posture from an uploaded image.
    Returns posture assessment and recommendations.
    """
    try:
        keypoints = await get_pose_keypoints(file)

        if not keypoints or len(keypoints) == 0:
            return {
                "status": "no_detection",
                "posture_quality": None,
                "issues": [],
                "keypoints": []
            }

        analysis = analyze_posture(keypoints)

        return {
            "status": "success",
            "posture_quality": analysis["quality"],
            "issues": analysis["issues"],
            "recommendations": analysis["recommendations"],
            "keypoints": keypoints
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing posture: {str(e)}")
