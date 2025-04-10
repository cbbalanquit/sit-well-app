import requests
import base64
import json
import os
from PIL import Image
import io

# API endpoints
api_base_url = "http://localhost:8000/api"
analyze_endpoint = f"{api_base_url}/posture/analyze"
upload_endpoint = f"{api_base_url}/posture/analyze/upload"

# Function to convert image file to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Function to save base64 image to file
def save_base64_to_image(base64_str, output_path):
    img_data = base64.b64decode(base64_str)
    with open(output_path, "wb") as f:
        f.write(img_data)
    print(f"Saved image to {output_path}")

# Test the base64 endpoint
def test_analyze_endpoint(image_path):
    print("\n=== Testing /api/posture/analyze endpoint ===")
    
    # Convert image to base64
    base64_image = image_to_base64(image_path)
    
    # Prepare request payload
    payload = {
        "image": base64_image
    }
    
    # Send request
    try:
        response = requests.post(analyze_endpoint, json=payload)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Is good posture: {result.get('isGoodPosture')}")
            print(f"Confidence: {result.get('confidence')}%")
            print("Feedback:")
            for item in result.get('feedback', []):
                print(f"- {item}")
            
            # Save returned image if available
            if result.get('img_with_pose'):
                save_base64_to_image(result['img_with_pose'], "api_result_pose.png")
            
            return result
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None

# Test the file upload endpoint
def test_upload_endpoint(image_path):
    print("\n=== Testing /api/posture/analyze/upload endpoint ===")
    
    # Prepare file for upload
    with open(image_path, 'rb') as img:
        files = {'file': (os.path.basename(image_path), img, 'image/jpeg')}
        
        # Send request
        try:
            response = requests.post(upload_endpoint, files=files)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Is good posture: {result.get('isGoodPosture')}")
                print(f"Confidence: {result.get('confidence')}%")
                print("Feedback:")
                for item in result.get('feedback', []):
                    print(f"- {item}")
                
                # Save returned image if available
                if result.get('img_with_pose'):
                    save_base64_to_image(result['img_with_pose'], "api_upload_result_pose.png")
                
                return result
            else:
                print(f"Error: {response.text}")
                return None
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return None

# Path to a sample image with a person sitting
image_path = "/root/codebase/sit-well-app/backend/inference-service/tests/test_images/improper-chair-sit-4.jpg"  # Replace with actual image path

# Ensure the image exists
if not os.path.exists(image_path):
    print(f"Warning: Image file '{image_path}' not found.")
    print("Please specify a valid image path.")
else:
    # Test both endpoints
    test_analyze_endpoint(image_path)
    test_upload_endpoint(image_path)
