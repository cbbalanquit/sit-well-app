import logging
import math
from typing import Dict, Any, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

def analyze_posture(keypoints: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """
    Analyze posture based on detected keypoints.
    
    Evaluates three key aspects:
    1. Shoulder balance - Are shoulders level?
    2. Neck position - Is neck in a neutral position?
    3. Back angle - Is the back upright?
    
    Args:
        keypoints: Dictionary of keypoints with coordinates and confidence
        
    Returns:
        Dictionary with analysis results and feedback
    """
    feedback = []
    scores = {
        "shoulder_balance": 0.0,
        "neck_position": 0.0,
        "back_position": 0.0
    }
    
    # Extract keypoint data for analysis (if available)
    left_shoulder = keypoints.get("left_shoulder")
    right_shoulder = keypoints.get("right_shoulder")
    left_hip = keypoints.get("left_hip")
    right_hip = keypoints.get("right_hip")
    left_ear = keypoints.get("left_ear")
    right_ear = keypoints.get("right_ear")
    
    # Analyze shoulder balance
    shoulder_balance_score, shoulder_feedback = analyze_shoulder_balance(left_shoulder, right_shoulder)
    scores["shoulder_balance"] = shoulder_balance_score
    if shoulder_feedback:
        feedback.append(shoulder_feedback)
    
    # Analyze neck position
    neck_position_score, neck_feedback = analyze_neck_position(left_ear, right_ear, left_shoulder, right_shoulder)
    scores["neck_position"] = neck_position_score
    if neck_feedback:
        feedback.append(neck_feedback)
    
    # Analyze back position
    back_position_score, back_feedback = analyze_back_position(left_shoulder, right_shoulder, left_hip, right_hip)
    scores["back_position"] = back_position_score
    if back_feedback:
        feedback.append(back_feedback)
    
    # Calculate overall score
    weights = {
        "shoulder_balance": 0.3,
        "neck_position": 0.4,
        "back_position": 0.3
    }
    
    overall_score = sum(scores[key] * weights[key] for key in scores) / sum(weights.values())
    
    # Generate overall assessment
    if overall_score > 0.8:
        feedback.append("Overall posture is excellent")
    elif overall_score > 0.6:
        feedback.append("Overall posture is good, with minor adjustments needed")
    else:
        feedback.append("Significant posture corrections needed")
    
    return {
        "shoulder_balance": scores["shoulder_balance"],
        "neck_position": scores["neck_position"],
        "back_position": scores["back_position"],
        "overall_score": overall_score,
        "is_good_posture": overall_score >= 0.7,
        "feedback": feedback
    }

def analyze_shoulder_balance(
    left_shoulder: Optional[Dict[str, float]], 
    right_shoulder: Optional[Dict[str, float]]
) -> (float, Optional[str]):
    """
    Analyze shoulder balance based on keypoints.
    
    Args:
        left_shoulder: Left shoulder keypoint
        right_shoulder: Right shoulder keypoint
        
    Returns:
        Tuple of score (0-1) and feedback message
    """
    if not (left_shoulder and right_shoulder):
        logger.warning("Missing shoulder keypoints for balance analysis")
        return 0.5, "Unable to assess shoulder balance"
    
    try:
        # Calculate height difference ratio
        shoulder_height_diff = abs(left_shoulder["y"] - right_shoulder["y"])
        shoulder_height_ratio = shoulder_height_diff / ((left_shoulder["y"] + right_shoulder["y"]) / 2)
        
        threshold = settings.SHOULDER_BALANCE_THRESHOLD
        
        if shoulder_height_ratio < threshold:
            return 1.0, "Shoulders are well-balanced"
        elif shoulder_height_ratio < threshold * 2:
            return 0.7, "Shoulders are slightly uneven"
        else:
            return 0.3, "Shoulders are significantly uneven - try to level them"
    except Exception as e:
        logger.error(f"Error analyzing shoulder balance: {str(e)}", exc_info=True)
        return 0.5, "Unable to analyze shoulder balance properly"

def analyze_neck_position(
    left_ear: Optional[Dict[str, float]], 
    right_ear: Optional[Dict[str, float]],
    left_shoulder: Optional[Dict[str, float]], 
    right_shoulder: Optional[Dict[str, float]]
) -> (float, Optional[str]):
    """
    Analyze neck position based on keypoints.
    
    Args:
        left_ear: Left ear keypoint
        right_ear: Right ear keypoint
        left_shoulder: Left shoulder keypoint
        right_shoulder: Right shoulder keypoint
        
    Returns:
        Tuple of score (0-1) and feedback message
    """
    # Need at least one ear and one shoulder
    ear = left_ear if left_ear else right_ear
    shoulder = left_shoulder if left_shoulder else right_shoulder
    
    if not (ear and shoulder):
        logger.warning("Missing ear or shoulder keypoints for neck analysis")
        return 0.5, "Unable to assess neck position"
    
    try:
        # Analyze forward/backward neck tilt
        neck_tilt = ear["x"] - shoulder["x"]
        vertical_distance = shoulder["y"] - ear["y"]
        
        if vertical_distance <= 0:
            # If ear is below shoulder (unusual), consider as poor posture
            return 0.3, "Head position is too low - raise your head"
        
        neck_distance_ratio = abs(neck_tilt) / vertical_distance
        threshold = settings.NECK_TILT_THRESHOLD
        
        if neck_distance_ratio < threshold:
            return 1.0, "Neck position is good"
        elif neck_distance_ratio < threshold * 2:
            if neck_tilt > 0:
                return 0.7, "Neck is slightly forward - try to align ears with shoulders"
            else:
                return 0.7, "Neck is slightly backward - try to align ears with shoulders"
        else:
            if neck_tilt > 0:
                return 0.3, "Neck is significantly forward - align your head over your shoulders"
            else:
                return 0.3, "Neck is significantly backward - align your head over your shoulders"
    except Exception as e:
        logger.error(f"Error analyzing neck position: {str(e)}", exc_info=True)
        return 0.5, "Unable to analyze neck position properly"

def analyze_back_position(
    left_shoulder: Optional[Dict[str, float]], 
    right_shoulder: Optional[Dict[str, float]],
    left_hip: Optional[Dict[str, float]], 
    right_hip: Optional[Dict[str, float]]
) -> (float, Optional[str]):
    """
    Analyze back position based on keypoints.
    
    Args:
        left_shoulder: Left shoulder keypoint
        right_shoulder: Right shoulder keypoint
        left_hip: Left hip keypoint
        right_hip: Right hip keypoint
        
    Returns:
        Tuple of score (0-1) and feedback message
    """
    # Use available shoulder and hip keypoints
    shoulder = left_shoulder if left_shoulder else right_shoulder
    hip = left_hip if left_hip else right_hip
    
    if not (shoulder and hip):
        logger.warning("Missing shoulder or hip keypoints for back analysis")
        return 0.5, "Unable to assess back position"
    
    try:
        # Calculate back angle (vertical is 90 degrees)
        dx = shoulder["x"] - hip["x"]
        dy = shoulder["y"] - hip["y"]
        
        # Convert to degrees from vertical
        back_angle = math.degrees(math.atan2(dx, -dy))  # Negative dy because y-axis is inverted
        
        threshold = settings.BACK_ANGLE_THRESHOLD
        
        if abs(back_angle) < threshold:
            return 1.0, "Back is upright - good posture"
        elif abs(back_angle) < threshold * 1.5:
            if back_angle > 0:
                return 0.7, "Back is leaning slightly backward - try to sit more upright"
            else:
                return 0.7, "Back is leaning slightly forward - try to sit more upright"
        else:
            if back_angle > 0:
                return 0.3, "Back is leaning too far back - adjust your chair"
            else:
                return 0.3, "Back is significantly hunched forward - sit up straighter"
    except Exception as e:
        logger.error(f"Error analyzing back position: {str(e)}", exc_info=True)
        return 0.5, "Unable to analyze back position properly"