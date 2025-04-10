// src/components/SitWellApp.js
import React, { useState, useEffect, useRef } from 'react';
import Header from './Header';
import ControlPanel from './ControlPanel';
import MediaViewer from './MediaViewer';
import OutputPanel from './OutputPanel';
import { useMediaQuery } from '../hooks/useMediaQuery';
import './SitWellApp.css';

const SitWellApp = () => {
  // State management
  const [mode, setMode] = useState('upload'); // 'upload' or 'live'
  const [liveMode, setLiveMode] = useState('capture'); // 'capture' or 'record'
  const [imageSource, setImageSource] = useState(null);
  const [isLiveActive, setIsLiveActive] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedCamera, setSelectedCamera] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingInterval, setRecordingInterval] = useState(null);
  
  const isMobile = useMediaQuery('(max-width: 768px)');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  
  // Toggle between upload and live modes
  const toggleMode = (selectedMode) => {
    if (isLiveActive && selectedMode === 'upload') {
      setIsLiveActive(false);
      if (isRecording) {
        handleStopRecording();
      }
    }
    setMode(selectedMode);
    setImageSource(null);
    setAnalysisResult(null);
  };
  
  // Handle file upload
  const handleFileUpload = (file) => {
    if (file) {
      setIsProcessing(true);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImageSource(e.target.result);
        // In a real app, you'd call your ML model here
        analyzePosture(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };
  
  // Process captured image
  const handleImageCapture = (imageData) => {
    setIsProcessing(true);
    setImageSource(imageData);
    analyzePosture(imageData);
  };
  
  // Update live status
  const handleLiveStatusChange = (status) => {
    setIsLiveActive(status);
    if (!status && isRecording) {
      handleStopRecording();
    }
  };
  
  // Start recording (continuous analysis)
  const handleStartRecording = () => {
    setIsRecording(true);
    
    // Set up interval for continuous analysis
    const interval = setInterval(() => {
      if (videoRef.current && canvasRef.current) {
        captureFrameForAnalysis();
      }
    }, 2000); // Analyze every 2 seconds
    
    setRecordingInterval(interval);
  };
  
  // Stop recording
  const handleStopRecording = () => {
    setIsRecording(false);
    
    if (recordingInterval) {
      clearInterval(recordingInterval);
      setRecordingInterval(null);
    }
  };
  
  // Capture frame for analysis without changing the view
  const captureFrameForAnalysis = () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const imageData = canvas.toDataURL('image/png');
    analyzePosture(imageData, true); // true means don't show loading
  };
  
  // Analyze posture (mock function - would connect to backend)
  const analyzePosture = (imageData, isBackground = false) => {
    if (!isBackground) {
      setIsProcessing(true);
    }
    
    // Mock analysis - in a real app, you'd call your backend/ML model
    setTimeout(() => {
      const postures = ['good', 'poor', 'good', 'poor', 'good'];
      const randomIndex = Math.floor(Math.random() * postures.length);
      const isGoodPosture = postures[randomIndex] === 'good';
      
      const feedback = [];
      
      if (isGoodPosture) {
        feedback.push("Shoulders are well-aligned");
        feedback.push("Neck is at a good angle");
        feedback.push("Back is properly supported");
        feedback.push("Screen height appears appropriate");
      } else {
        feedback.push("Shoulders appear slightly hunched");
        feedback.push("Neck is tilted forward too much");
        feedback.push("Lower back needs better support");
        feedback.push("Consider raising your screen height");
      }
      
      const results = {
        isGoodPosture,
        confidence: 70 + Math.floor(Math.random() * 20),
        feedback,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setAnalysisResult(results);
      if (!isBackground) {
        setIsProcessing(false);
      }
    }, isBackground ? 500 : 1000); // Shorter delay for background analysis
  };
  
  // Reset the analysis and image
  const resetAnalysis = () => {
    setImageSource(null);
    setAnalysisResult(null);
  };
  
  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (recordingInterval) {
        clearInterval(recordingInterval);
      }
    };
  }, [recordingInterval]);
  
  return (
    <div className="sit-well-app">
      <Header />
      
      <main className="app-content">
        <div className={`content-container ${isMobile ? 'mobile-layout' : 'desktop-layout'}`}>
          <ControlPanel 
            mode={mode}
            liveMode={liveMode}
            toggleMode={toggleMode}
            setLiveMode={setLiveMode}
            handleFileUpload={handleFileUpload}
            isLiveActive={isLiveActive}
            selectedCamera={selectedCamera}
            setSelectedCamera={setSelectedCamera}
            handleStartRecording={handleStartRecording}
            handleStopRecording={handleStopRecording}
            isRecording={isRecording}
          />
          
          <MediaViewer 
            mode={mode}
            liveMode={liveMode}
            imageSource={imageSource}
            isLiveActive={isLiveActive}
            isProcessing={isProcessing}
            onImageCapture={handleImageCapture}
            onLiveStatusChange={handleLiveStatusChange}
            selectedCamera={selectedCamera}
            resetAnalysis={resetAnalysis}
            isRecording={isRecording}
            videoRef={videoRef}
            canvasRef={canvasRef}
          />
          
          <OutputPanel 
            analysisResult={analysisResult} 
          />
        </div>
      </main>
      
      <footer className="app-footer">
        <p>SIT WELL APP &copy; {new Date().getFullYear()} - Your Posture Assistant</p>
      </footer>
    </div>
  );
};

export default SitWellApp;