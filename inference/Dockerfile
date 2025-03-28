FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir ultralytics fastapi uvicorn python-multipart opencv-python

COPY . .

EXPOSE 8000

CMD ["uvicorn", "infer_yolo:app", "--host", "0.0.0.0", "--port", "8000"]