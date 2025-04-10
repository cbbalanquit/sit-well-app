// src/components/SitWellApp.js
import React, { useState, useEffect, useRef } from 'react';
import PostureService from '../services/PostureService';
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
  const [isLoading, setIsLoading] = useState(false);
  const [analysisInterval, setAnalysisInterval] = useState(null);
  
  const isMobile = useMediaQuery('(max-width: 768px)');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const toggleRecording = () => {
    setIsRecording(prev => !prev);
  };
  
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
  const handleFileUpload = async (file) => {
    if (file) {
      try {
        // Show loading state
        setIsLoading(true);
        
        // First, display the original image
        const reader = new FileReader();
        reader.onload = (e) => {
          setImageSource(e.target.result);
        };
        reader.readAsDataURL(file);
        
        // Send to backend for analysis
        const result = await PostureService.analyzeImageFile(file);
        
        // Update the image with pose overlay
        if (result.img_with_pose) {
          setImageSource(`data:image/png;base64,${result.img_with_pose}`);
        }
        
        // Update analysis results
        setAnalysisResult({
          isGoodPosture: result.isGoodPosture,
          confidence: result.confidence,
          feedback: result.feedback
        });
      } catch (error) {
        console.error('Error analyzing image:', error);
        setAnalysisResult({
          isGoodPosture: false,
          confidence: 0,
          feedback: ['Error analyzing posture. Please try again.']
        });
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleAnalysisResult = (result) => {
    setAnalysisResult(result);
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
    }, 2000); // Analyze every second
    
    setAnalysisInterval(interval);
  };
  
  // Stop recording
  const handleStopRecording = () => {
    setIsRecording(false);
    
    if (analysisInterval) {
      clearInterval(analysisInterval);
      setAnalysisInterval(null);
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
  const analyzePosture = async (imageData, isBackground = false) => {
    if (!isBackground) {
      setIsProcessing(true);
    }
    
    try {
      // Send to backend API for analysis
      const result = await PostureService.analyzeImageData(imageData);
      
      // Update analysis results
      setAnalysisResult({
        isGoodPosture: result.isGoodPosture,
        confidence: result.confidence,
        feedback: result.feedback,
        timestamp: new Date().toLocaleTimeString()
      });
      
      // If this was from capture mode and result has an image, update the display
      if (!isBackground && result.img_with_pose) {
        setImageSource(`data:image/png;base64,${result.img_with_pose}`);
      }
    } catch (error) {
      console.error('Error analyzing posture:', error);
      setAnalysisResult({
        isGoodPosture: false,
        confidence: 0,
        feedback: ['Error analyzing posture. Please try again.'],
        timestamp: new Date().toLocaleTimeString()
      });
    } finally {
      if (!isBackground) {
        setIsProcessing(false);
      }
    }
  };
  
  // Reset the analysis and image
  const resetAnalysis = () => {
    setImageSource(null);
    setAnalysisResult(null);
  };
  
  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (analysisInterval) {
        clearInterval(analysisInterval);
      }
    };
  }, [analysisInterval]);
  
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
            toggleRecording={toggleRecording}
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
            onAnalysisResult={handleAnalysisResult}
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