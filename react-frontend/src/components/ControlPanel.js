// src/components/ControlPanel.js
import React, { useRef, useEffect, useState } from 'react';
import './ControlPanel.css';

const ControlPanel = ({ 
  mode, 
  liveMode, 
  toggleMode, 
  setLiveMode, 
  handleFileUpload, 
  isLiveActive,
  cameras,
  selectedCamera,
  setSelectedCamera,
  handleStartRecording,
  handleStopRecording,
  isRecording,
  toggleRecording
}) => {
  const fileInputRef = useRef(null);
  const [availableCameras, setAvailableCameras] = useState([]);

  // Refresh cameras list when component mounts
  useEffect(() => {
    refreshCameras();
  }, []);

  const triggerFileUpload = () => {
    fileInputRef.current.click();
  };
  
  // Function to get available cameras
  const refreshCameras = async () => {
    try {
      // First request permission if needed
      await navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          // Stop the stream immediately after getting permission
          stream.getTracks().forEach(track => track.stop());
        })
        .catch(err => {
          console.error("Camera permission denied:", err);
        });
      
      // Then enumerate devices
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      
      console.log('Available cameras:', videoDevices);
      setAvailableCameras(videoDevices);
      
      // Set default camera if available and not already set
      if (videoDevices.length > 0 && !selectedCamera) {
        setSelectedCamera(videoDevices[0].deviceId);
      }
    } catch (error) {
      console.error('Error getting camera devices:', error);
    }
  };
  
  return (
    <div className="control-panel">
      <h2 className="panel-title">
        <span className="icon">📋</span> Controls
      </h2>
      
      <div className="control-section">
        <label className="section-label">Input Mode</label>
        <div className="mode-buttons">
          <button 
            className={`mode-button ${mode === 'upload' ? 'active' : ''}`} 
            onClick={() => toggleMode('upload')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="button-icon">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <span>Upload</span>
          </button>
          <button 
            className={`mode-button ${mode === 'live' ? 'active' : ''}`} 
            onClick={() => toggleMode('live')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="button-icon">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
              <circle cx="12" cy="13" r="4"></circle>
            </svg>
            <span>Live</span>
          </button>
        </div>
      </div>
      
      {mode === 'upload' && (
        <div className="upload-section">
          <div className="upload-area" onClick={triggerFileUpload}>
            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <p className="upload-text">Drag & drop an image or click to browse</p>
            <button className="browse-button">Browse</button>
            <input 
              ref={fileInputRef}
              type="file" 
              accept="image/*" 
              onChange={(e) => handleFileUpload(e.target.files[0])} 
              className="hidden-input" 
            />
          </div>
        </div>
      )}
      
      {mode === 'live' && (
        <div className="live-controls">
          <div className="camera-selection">
            <div className="section-header">
              <label className="section-label">Camera Source</label>
              <button className="refresh-button" onClick={refreshCameras} title="Refresh camera list">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
                </svg>
              </button>
            </div>
            
            {availableCameras.length > 0 ? (
              <select 
                className="camera-select"
                value={selectedCamera}
                onChange={(e) => setSelectedCamera(e.target.value)}
              >
                {availableCameras.map((camera) => (
                  <option key={camera.deviceId} value={camera.deviceId}>
                    {camera.label || `Camera ${availableCameras.indexOf(camera) + 1}`}
                  </option>
                ))}
              </select>
            ) : (
              <div className="no-cameras">
                <p>No cameras found</p>
                <button className="refresh-cameras-button" onClick={refreshCameras}>
                  Refresh Cameras
                </button>
              </div>
            )}
          </div>
          
          <div className="capture-mode">
            <label className="section-label">Capture Mode</label>
            <div className="mode-buttons">
              <button 
                className={`capture-button ${liveMode === 'capture' ? 'active' : ''}`}
                onClick={() => setLiveMode('capture')}
              >
                <span>Capture</span>
              </button>
              <button 
                className={`capture-button ${liveMode === 'record' ? 'active' : ''}`}
                onClick={() => setLiveMode('record')}
              >
                <span>Record</span>
              </button>
            </div>
          </div>
          
          {/* Recording controls */}
          {liveMode === 'record' && isLiveActive && (
            <div className="record-controls">
              {!isRecording ? (
                <button 
                  className="start-record-button"
                  onClick={handleStartRecording}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="button-icon">
                    <circle cx="12" cy="12" r="10" />
                    <polygon points="10 8 16 12 10 16 10 8" fill="currentColor" />
                  </svg>
                  Start Recording
                </button>
              ) : (
                <button 
                  className="stop-record-button"
                  onClick={handleStopRecording}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="button-icon">
                    <circle cx="12" cy="12" r="10" />
                    <rect x="9" y="9" width="6" height="6" fill="currentColor" />
                  </svg>
                  Stop Recording
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ControlPanel;