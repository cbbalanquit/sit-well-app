import io

from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
import cv2
import numpy as np

app = FastAPI()
model = YOLO('yolo11n-pose.pt')

@app.post("/detect_pose")
async def detect_pose(file: UploadFile = File(...)):
    """
    Detect keypoints using Pose Estimation model
    
    Args:
        file (UploadFile): image file uploaded
        
    Returns:
        dict: the status of inference
    """
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = model(img)

    if len(results) > 0 and results[0].keypoints is not None:
        keypoints = results[0].keypoints.data.tolist()
        return {"status": "success", "keypoints": keypoints}

    return {"status": "no_detection", "keypoints": []}
