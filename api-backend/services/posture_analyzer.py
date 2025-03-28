import numpy as np
from typing import List, Dict, Any

def calculate_angle(a, b, c):
    """
    Calculate angle between three points (in degrees).
    Points are in format [x, y, confidence]
    """
    a = np.array([a[0], a[1]])
    b = np.array([b[0], b[1]])
    c = np.array([c[0], c[1]])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

    return np.degrees(angle)

def analyze_posture(keypoints: List) -> Dict[str, Any]:
    """
    Analyze posture using keypoints.
    Returns posture quality, issues, and recommendations.
    
    YOLO keypoints order:
    0: nose, 1: left_eye, 2: right_eye, 3: left_ear, 4: right_ear, 
    5: left_shoulder, 6: right_shoulder, 7: left_elbow, 8: right_elbow,
    9: left_wrist, 10: right_wrist, 11: left_hip, 12: right_hip,
    13: left_knee, 14: right_knee, 15: left_ankle, 16: right_ankle
    """
    issues = []
    recommendations = []

    person = keypoints[0]

    required_points = [0, 5, 6, 11, 12]  # nose, shoulders, hips
    if not all(i < len(person) and person[i][2] > 0.5 for i in required_points):
        # Not enough confidence in the required keypoints
        return {
            "quality": "unknown",
            "issues": ["Not enough visible keypoints for analysis"],
            "recommendations": ["Position yourself so your upper body is clearly visible"]
        }

    # Extract key points
    nose = person[0]
    left_shoulder = person[5]
    right_shoulder = person[6]
    left_hip = person[11]
    right_hip = person[12]

    # 1. Check neck angle (using nose and midpoint between shoulders)
    mid_shoulder = [(left_shoulder[0] + right_shoulder[0])/2, 
                    (left_shoulder[1] + right_shoulder[1])/2,
                    1.0]

    # Create a vertical reference point below mid_shoulder
    vertical_ref = [mid_shoulder[0], mid_shoulder[1] + 100, 1.0]

    # Neck angle from vertical
    neck_angle = calculate_angle(nose, mid_shoulder, vertical_ref)

    # 2. Check shoulder alignment (horizontal)
    shoulder_angle = abs(90 - calculate_angle(
        [left_shoulder[0], left_shoulder[1] - 100, 1.0],
        left_shoulder,
        right_shoulder
    ))

    # 3. Check back angle (using midpoints of shoulders and hips)
    mid_hip = [(left_hip[0] + right_hip[0])/2, 
               (left_hip[1] + right_hip[1])/2,
               1.0]

    # Create a vertical reference point below mid_hip
    hip_vertical_ref = [mid_hip[0], mid_hip[1] + 100, 1.0]

    # Back angle from vertical
    back_angle = calculate_angle(mid_shoulder, mid_hip, hip_vertical_ref)

    # Analyze angles and create feedback
    if neck_angle > 45:
        issues.append("Forward head posture")
        recommendations.append("Bring your head back to align with your spine")

    if shoulder_angle > 15:
        issues.append("Uneven shoulders")
        recommendations.append("Level your shoulders and relax them down")

    if back_angle > 20:
        issues.append("Slouching")
        recommendations.append("Sit up straight with your back against the chair")

    # Determine overall posture quality
    if len(issues) == 0:
        quality = "good"
    elif len(issues) == 1:
        quality = "fair"
    else:
        quality = "poor"

    return {
        "quality": quality,
        "issues": issues,
        "recommendations": recommendations
    }
