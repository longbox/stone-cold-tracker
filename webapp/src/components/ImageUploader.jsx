"use client";

import { useState, useRef } from 'react';
import { Upload, ImageIcon, ChevronRight } from 'lucide-react';
import ResultsDisplay from './ResultsDisplay';

export default function ImageUploader() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      setFile(droppedFile);
      setPreviewUrl(URL.createObjectURL(droppedFile));
      setResult(null);
      setError(null);
    }
  };

  const analyzeImage = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze image. Ensure your API key is set.');
      }

      const data = await response.json();
      setResult(data.analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div 
        className="glass-panel" 
        style={{ 
          padding: '3rem 2rem', 
          textAlign: 'center',
          cursor: 'pointer',
          border: '2px dashed rgba(255,255,255,0.2)',
          transition: 'all 0.2s ease'
        }}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          accept="image/*" 
          style={{ display: 'none' }} 
        />
        
        {previewUrl ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <img 
              src={previewUrl} 
              alt="Preview" 
              style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '12px', objectFit: 'cover' }} 
            />
            <p style={{ color: 'rgba(255,255,255,0.7)' }}>Click or drag to replace image</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <div style={{ 
              width: '80px', height: '80px', borderRadius: '50%', 
              background: 'rgba(139, 92, 246, 0.2)', display: 'flex', 
              alignItems: 'center', justifyContent: 'center' 
            }}>
              <Upload size={32} color="#8b5cf6" />
            </div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Drop your photo here</h3>
            <p style={{ color: 'rgba(255,255,255,0.6)' }}>or click to browse your files</p>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <button 
          className="btn-primary" 
          onClick={analyzeImage} 
          disabled={!file || isLoading}
          style={{ width: '100%', maxWidth: '300px', padding: '16px' }}
        >
          {isLoading ? (
            <>
              <div className="spinner"></div> Analyzing...
            </>
          ) : (
            <>
              Analyze Oxalate Content <ChevronRight size={20} />
            </>
          )}
        </button>
      </div>

      {error && (
        <div style={{ 
          background: 'rgba(239, 68, 68, 0.1)', 
          border: '1px solid rgba(239, 68, 68, 0.3)', 
          padding: '1rem', borderRadius: '12px', color: '#fca5a5',
          textAlign: 'center'
        }}>
          {error}
        </div>
      )}

      {result && <ResultsDisplay result={result} />}
    </div>
  );
}
