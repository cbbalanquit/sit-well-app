// src/components/MediaViewer.js
import React, { useState, useRef, useEffect } from 'react';
import './MediaViewer.css';

const MediaViewer = ({ 
  mode, 
  liveMode, 
  imageSource, 
  isLiveActive, 
  isProcessing,
  onImageCapture, 
  onLiveStatusChange,
  selectedCamera,
  resetAnalysis,
  isRecording
}) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [cameraError, setCameraError] = useState(null);
  
  // Start or stop live camera stream based on mode
  useEffect(() => {
    if (mode === 'live' && !isLiveActive) {
      startLiveStream();
    } else if (mode !== 'live') {
      stopLiveStream();
    }
    
    return () => {
      if (stream) {
        stopLiveStream();
      }
    };
  }, [mode]);
  
  // Update stream when camera selection changes
  useEffect(() => {
    if (mode === 'live' && isLiveActive && selectedCamera) {
      stopLiveStream();
      startLiveStream();
    }
  }, [selectedCamera]);
  
  // Start live camera stream
  const startLiveStream = async () => {
    try {
      if (stream) {
        stopLiveStream();
      }
      
      // Get camera constraints
      const constraints = { 
        video: {
          deviceId: selectedCamera ? { exact: selectedCamera } : undefined,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      };
      
      console.log('Accessing camera with constraints:', constraints);
      const newStream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log('Camera stream obtained:', newStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = newStream;
        setStream(newStream);
        onLiveStatusChange(true);
        setCameraError(null);
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      setCameraError(error.message || 'Could not access camera');
      onLiveStatusChange(false);
    }
  };
  
  // Stop live camera stream
  const stopLiveStream = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
      setStream(null);
      onLiveStatusChange(false);
    }
  };
  
  // Capture single frame for analysis
  const captureFrame = () => {
    if (canvasRef.current && videoRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      const imageData = canvas.toDataURL('image/png');
      onImageCapture(imageData);
    }
  };
  
  return (
    <div className="media-viewer">
      <div className="viewer-header">
        <h2 className="panel-title">
          <span className="icon">🎥</span> Image/Video Viewer
        </h2>
      </div>
      
      <div className="viewer-content">
        {mode === 'upload' && imageSource ? (
          <img src={imageSource} alt="Uploaded" className="display-image" />
        ) : mode === 'live' ? (
          <>
            {cameraError ? (
              <div className="camera-error">
                <p>Camera Error: {cameraError}</p>
                <button onClick={startLiveStream} className="retry-button">
                  Retry Camera Access
                </button>
              </div>
            ) : (
              <>
                <video 
                  ref={videoRef} 
                  autoPlay 
                  playsInline
                  muted 
                  className={`display-video ${!isLiveActive || (liveMode === 'capture' && imageSource) ? 'hidden' : ''}`}
                />
                {liveMode === 'capture' && imageSource && (
                  <img src={imageSource} alt="Captured" className="display-image" />
                )}
              </>
            )}
          </>
        ) : (
          <div className="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
              <circle cx="12" cy="13" r="4"></circle>
            </svg>
            <p className="empty-text">No image available</p>
          </div>
        )}
        
        {/* Loading overlay */}
        {isProcessing && (
          <div className="processing-overlay">
            <div className="processing-indicator">
              <div className="spinner"></div>
              <p>Analyzing posture...</p>
            </div>
          </div>
        )}
        
        {/* Hidden canvas for capturing frames */}
        <canvas ref={canvasRef} className="hidden-canvas" />
        
        {/* Recording indicator */}
        {mode === 'live' && liveMode === 'record' && isRecording && (
          <div className="recording-indicator">
            <div className="recording-dot"></div>
            <span>Recording</span>
          </div>
        )}
      </div>
      
      {/* Capture button for live mode */}
      {mode === 'live' && liveMode === 'capture' && isLiveActive && !imageSource && (
        <div className="capture-controls">
          <button 
            className="capture-photo-button"
            onClick={captureFrame}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="button-icon">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
              <circle cx="12" cy="13" r="4"></circle>
            </svg>
            Take Photo
          </button>
        </div>
      )}
      
      {/* Show retry button if image is already captured */}
      {mode === 'live' && liveMode === 'capture' && imageSource && (
        <div className="capture-controls">
          <button 
            className="retry-button"
            onClick={resetAnalysis}
          >
            Take Another Photo
          </button>
        </div>
      )}
      
      {/* Media controls */}
      {(imageSource || isLiveActive) && (
        <div className="media-controls">
          {imageSource && mode === 'upload' && (
            <button 
              className="control-button"
              onClick={resetAnalysis}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="button-icon">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              Clear
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default MediaViewer;