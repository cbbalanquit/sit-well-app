import os
import base64
import cv2
import numpy as np
import logging
from typing import Dict, Any, List, Optional
import functools

from ultralytics import YOLO
from app.core.config import settings
from app.core.errors import ModelError, ImageProcessingError, NoPersonDetectedError

logger = logging.getLogger(__name__)

# Define keypoint mapping
KEYPOINT_DICT = {
    0: "nose",
    1: "left_eye", 
    2: "right_eye",
    3: "left_ear",
    4: "right_ear",
    5: "left_shoulder",
    6: "right_shoulder", 
    7: "left_elbow",
    8: "right_elbow",
    9: "left_wrist", 
    10: "right_wrist",
    11: "left_hip",
    12: "right_hip",
    13: "left_knee",
    14: "right_knee",
    15: "left_ankle",
    16: "right_ankle"
}

class PoseDetector:
    """Service for detecting human pose using YOLOv8."""
    
    def __init__(self, model_path: str = settings.MODEL_PATH, conf: float = settings.MODEL_CONFIDENCE):
        """
        Initialize pose detector with model.
        
        Args:
            model_path: Path to YOLOv8 pose model
            conf: Confidence threshold for detections
        """
        try:
            # Check if the model file exists
            if not os.path.exists(model_path):
                logger.info(f"Model file {model_path} not found. Downloading...")
                
                # If it's a local path, create directory if needed
                if "/" in model_path:
                    os.makedirs(os.path.dirname(model_path), exist_ok=True)
                
                # Use standard model name if not a full path (let YOLO handle download)
                if not os.path.isabs(model_path) and "/" not in model_path:
                    logger.info(f"Using standard model: {model_path}")
                else:
                    logger.info(f"Downloading model to: {model_path}")
            
            logger.info(f"Loading YOLO model: {model_path}")
            self.model = YOLO(model_path)
            self.conf = conf
            self.model_name = model_path
            logger.info(f"Model loaded successfully: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}", exc_info=True)
            # Try fallback to standard model name
            try:
                fallback_model = "yolov8n-pose.pt"
                logger.info(f"Attempting to load fallback model: {fallback_model}")
                self.model = YOLO(fallback_model)
                self.conf = conf
                self.model_name = fallback_model
                logger.info(f"Fallback model loaded successfully: {fallback_model}")
            except Exception as fallback_error:
                logger.error(f"Failed to load fallback model: {str(fallback_error)}", exc_info=True)
                raise ModelError(f"Failed to load model: {str(e)} and fallback also failed: {str(fallback_error)}")
    
    def decode_base64_image(self, base64_string: str) -> np.ndarray:
        """
        Decode base64 image to OpenCV format.
        
        Args:
            base64_string: Base64 encoded image
            
        Returns:
            Image as numpy array
            
        Raises:
            ImageProcessingError: If image decoding fails
        """
        try:
            # Remove data URL prefix if present
            if "base64," in base64_string:
                base64_string = base64_string.split("base64,")[1]
            
            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_string)
            
            # Convert to numpy array
            np_array = np.frombuffer(image_bytes, np.uint8)
            
            # Decode to image
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ImageProcessingError("Failed to decode image")
                
            return image
        except Exception as e:
            logger.error(f"Error decoding image: {str(e)}", exc_info=True)
            raise ImageProcessingError(f"Error decoding image: {str(e)}")
    
    def encode_image_to_base64(self, image: np.ndarray) -> str:
        """
        Encode OpenCV image to base64 string.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Base64 encoded image
            
        Raises:
            ImageProcessingError: If image encoding fails
        """
        try:
            success, encoded_image = cv2.imencode('.png', image)
            if not success:
                raise ImageProcessingError("Failed to encode image")
                
            return base64.b64encode(encoded_image).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}", exc_info=True)
            raise ImageProcessingError(f"Error encoding image: {str(e)}")
    
    def detect_pose(self, image_data: str) -> Dict[str, Any]:
        """
        Detect pose in image and extract keypoints.
        
        Args:
            image_data: Base64 encoded image
            
        Returns:
            Dictionary with keypoints and annotated image
            
        Raises:
            NoPersonDetectedError: If no person is detected
            ModelError: If model inference fails
            ImageProcessingError: If image processing fails
        """
        try:
            # Decode image
            img = self.decode_base64_image(image_data)
            
            # Run inference
            results = self.model(img, verbose=False, conf=self.conf)
            
            # Check if pose was detected
            if len(results) == 0 or len(results[0].keypoints.xy) == 0:
                raise NoPersonDetectedError()
            
            # Get first result
            result = results[0]
            
            # Get keypoints for first person
            keypoints = result.keypoints.xy[0].cpu().numpy()
            confidences = result.keypoints.conf[0].cpu().numpy()
            
            # Convert keypoints to dictionary
            keypoints_dict = {}
            for i, (x, y) in enumerate(keypoints):
                conf = float(confidences[i])
                if conf > 0.5:  # Only include keypoints with confidence > 0.5
                    keypoints_dict[KEYPOINT_DICT[i]] = {
                        "x": float(x),
                        "y": float(y),
                        "confidence": conf
                    }
            
            # Draw pose on image
            annotated_img = result.plot()
            
            # Convert back to base64
            img_base64 = self.encode_image_to_base64(annotated_img)
            
            return {
                "keypoints": keypoints_dict,
                "img_with_pose": img_base64
            }
        except NoPersonDetectedError:
            raise
        except Exception as e:
            logger.error(f"Error in pose detection: {str(e)}", exc_info=True)
            raise ModelError(f"Error in pose detection: {str(e)}")

# Singleton instance to share across requests
_pose_detector_instance = None

def get_pose_detector() -> PoseDetector:
    """
    Get or create singleton instance of PoseDetector.
    
    Returns:
        PoseDetector instance
    """
    global _pose_detector_instance
    if _pose_detector_instance is None:
        _pose_detector_instance = PoseDetector()
    return _pose_detector_instance