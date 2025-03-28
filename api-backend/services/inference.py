import io

import aiohttp
from fastapi import UploadFile
import cv2
import numpy as np

# INFERENCE_URL = "http://inference:8000/detect_pose"  # Use container name in Docker
# For local development, use:
INFERENCE_URL = "http://localhost:8000/detect_pose"

async def get_pose_keypoints(file: UploadFile):
    """
    Send image to inference service and get keypoints.
    """
    content = await file.read()

    # Reset file pointer for potential reuse
    await file.seek(0)

    async with aiohttp.ClientSession() as session:
        form_data = aiohttp.FormData()
        form_data.add_field('file', content, filename=file.filename)

        async with session.post(INFERENCE_URL, data=form_data) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("keypoints", [])

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
