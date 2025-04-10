// src/components/OutputPanel.js
import React from 'react';
import './OutputPanel.css';

const OutputPanel = ({ analysisResult }) => {
  return (
    <div className="output-panel">
      <h2 className="panel-title">
        <span className="icon">📊</span> Analysis
      </h2>
      
      {analysisResult ? (
        <div className="analysis-content">
          {/* Status indicator */}
          <div className={`status-container ${analysisResult.isGoodPosture ? 'good' : 'poor'}`}>
            <div className="status-header">
              <div className="status-indicator"></div>
              <h3 className="status-title">
                {analysisResult.isGoodPosture ? 'Good Sitting Position' : 'Poor Sitting Position'}
              </h3>
            </div>
            
            <div className="confidence-meter">
              <div className="confidence-label">Confidence</div>
              <div className="confidence-bar-container">
                <div 
                  className="confidence-bar"
                  style={{ width: `${analysisResult.confidence}%` }}
                ></div>
              </div>
              <div className="confidence-value">{analysisResult.confidence}%</div>
            </div>
            
            <div className="timestamp">
              Analyzed at {analysisResult.timestamp}
            </div>
          </div>
          
          {/* Detailed feedback */}
          <div className="feedback-section">
            <h4 className="section-title">Posture Analysis:</h4>
            <ul className="feedback-list">
              {analysisResult.feedback.map((item, index) => (
                <li key={index} className="feedback-item">
                  <span className={`feedback-icon ${analysisResult.isGoodPosture ? 'good' : 'poor'}`}>
                    {analysisResult.isGoodPosture ? '✓' : '!'}
                  </span>
                  <span className="feedback-text">{item}</span>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Recommendations */}
          <div className="recommendations">
            <h4 className="section-title">Recommendations:</h4>
            <p className="recommendation-text">
              {analysisResult.isGoodPosture 
                ? "Great job maintaining proper posture! Remember to take short breaks every 30 minutes to stretch and rest your eyes."
                : "Try adjusting your chair height and monitor position. Keep your back against the chair, feet flat on the floor, and screen at eye level."
              }
            </p>
          </div>
        </div>
      ) : (
        <div className="empty-analysis">
          <div className="empty-icon-container">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
              <line x1="8" y1="21" x2="16" y2="21"></line>
              <line x1="12" y1="17" x2="12" y2="21"></line>
            </svg>
          </div>
          <p className="empty-text">
            Upload an image or use the camera<br />to analyze your sitting position
          </p>
        </div>
      )}
    </div>
  );
};

export default OutputPanel;