import json
import base64

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
from services.inference import get_pose_keypoints_from_image
from services.posture_analyzer import analyze_posture

router = APIRouter(tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)

            if "image" in json_data:
                # Decode base64 image
                img_data = base64.b64decode(json_data["image"].split(",")[1])
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Process with inference service
                keypoints = await get_pose_keypoints_from_image(img)

                # Analyze posture
                if keypoints and len(keypoints) > 0:
                    analysis = analyze_posture(keypoints)

                    # Send results back to client
                    await websocket.send_json({
                        "status": "success",
                        "posture_quality": analysis["quality"],
                        "issues": analysis["issues"],
                        "recommendations": analysis["recommendations"],
                        "keypoints": keypoints
                    })
                else:
                    await websocket.send_json({
                        "status": "no_detection",
                        "posture_quality": None,
                        "issues": [],
                        "recommendations": [],
                        "keypoints": []
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
