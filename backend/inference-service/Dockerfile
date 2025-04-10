FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create model directory
RUN mkdir -p /app/models

# Copy the application code
COPY app/ ./app/

# Download YOLOv8 model
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n-pose.pt').save('/app/models/')"

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/app/models/yolov8n-pose.pt

# Expose the port
EXPOSE 8001

# Start the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]