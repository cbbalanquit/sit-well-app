import io

import aiohttp
from fastapi import UploadFile
import cv2
import numpy as np

# INFERENCE_URL = "http://inference:8000/detect_pose"  # Use container name in Docker
# For local development, use:
INFERENCE_URL = "http://localhost:8000/detect_pose"

def draw_pose_on_image(image, keypoints):
    """Draw skeleton and keypoints on the image."""
    # Define the connections between keypoints for skeleton
    skeleton = [
        [0, 1], [0, 2], [1, 3], [2, 4],  # Face
        [5, 6], [5, 11], [6, 12],  # Torso
        [5, 7], [7, 9], [6, 8], [8, 10],  # Arms
        [11, 13], [13, 15], [12, 14], [14, 16]  # Legs
    ]

    colors = {
        'nose': (0, 0, 255),        # Red
        'shoulders': (0, 255, 0),   # Green
        'elbows': (255, 0, 0),      # Blue
        'wrists': (255, 255, 0),    # Yellow
        'hips': (255, 0, 255),      # Purple
        'knees': (0, 255, 255),     # Cyan
        'ankles': (255, 255, 255)   # White
    }

    img_with_keypoints = image.copy()

    if keypoints and len(keypoints) > 0:
        person_keypoints = keypoints[0]
        
        # Draw keypoints
        for i, (x, y, conf) in enumerate(person_keypoints):
            if conf > 0.5:  # Only draw high-confidence points
                point_color = (0, 255, 0)  # Default green
                radius = 5

                if i == 0:  # Nose
                    point_color = colors['nose']
                    radius = 4
                elif i in [5, 6]:  # Shoulders
                    point_color = colors['shoulders']
                    radius = 6
                elif i in [11, 12]:  # Hips
                    point_color = colors['hips']
                    radius = 6

                cv2.circle(img_with_keypoints, (int(x), int(y)), radius, point_color, -1)

        # Draw skeleton connections
        for connection in skeleton:
            start_idx, end_idx = connection

            if (start_idx < len(person_keypoints) and end_idx < len(person_keypoints) and
                person_keypoints[start_idx][2] > 0.5 and person_keypoints[end_idx][2] > 0.5):

                start_point = (int(person_keypoints[start_idx][0]), int(person_keypoints[start_idx][1]))
                end_point = (int(person_keypoints[end_idx][0]), int(person_keypoints[end_idx][1]))

                cv2.line(img_with_keypoints, start_point, end_point, (102, 204, 255), 2)

    return img_with_keypoints

async def get_pose_keypoints(file: UploadFile):
    """
    Send image to inference service and get keypoints.
    """
    content = await file.read()

    # Convert to image for drawing
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Reset file pointer for reuse
    await file.seek(0)
    
    # Your existing code to call inference service
    async with aiohttp.ClientSession() as session:
        form_data = aiohttp.FormData()
        form_data.add_field('file', content, filename=file.filename)

        async with session.post(INFERENCE_URL, data=form_data) as response:
            if response.status == 200:
                result = await response.json()
                keypoints = result.get("keypoints", [])

                # Draw keypoints on image if any detected
                if keypoints and len(keypoints) > 0:
                    annotated_img = draw_pose_on_image(img, keypoints)

                    # Convert the annotated image to base64 for sending to frontend
                    _, buffer = cv2.imencode('.jpg', annotated_img)
                    img_str = base64.b64encode(buffer).decode('utf-8')

                    # Add the annotated image to the result
                    result["annotated_image"] = f"data:image/jpeg;base64,{img_str}"

                return result
            else:
                error_text = await response.text()
                raise Exception(f"Inference service error: {response.status} - {error_text}")

async def get_pose_keypoints_from_image(img):
    """
    Send OpenCV image to inference service and get keypoints.
    """
    # Encode image to byte array
    is_success, buffer = cv2.imencode(".jpg", img)
    if not is_success:
        raise Exception("Failed to encode image")

    # Convert to bytes
    content = io.BytesIO(buffer).getvalue()

    async with aiohttp.ClientSession() as session:
        form_data = aiohttp.FormData()
        form_data.add_field('file', content, filename='frame.jpg')

        async with session.post(INFERENCE_URL, data=form_data) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("keypoints", [])

            error_text = await response.text()
            raise Exception(f"Inference service error: {response.status} - {error_text}")
