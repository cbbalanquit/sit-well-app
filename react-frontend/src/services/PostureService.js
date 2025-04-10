// src/services/PostureService.js

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Analyze an image using base64 encoding
 */
export const analyzeImageData = async (imageData) => {
  try {
    const response = await fetch(`${API_URL}/api/posture/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: imageData }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error analyzing image:', error);
    throw error;
  }
};

/**
 * Upload and analyze an image file
 */
export const analyzeImageFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/api/posture/analyze/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading image:', error);
    throw error;
  }
};

export default {
  analyzeImageData,
  analyzeImageFile,
};