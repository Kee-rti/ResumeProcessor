import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, Check } from 'lucide-react';
import './resumeupload.css';

const ResumeUpload = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.type === 'application/pdf' || 
        selectedFile.type === 'application/msword' || 
        selectedFile.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please select a PDF or Word document.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('resume', file);

    try {
      const response = await fetch('http://localhost:8000/api/extract_resume/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      setError(null);
    } catch (err) {
      console.error('Error:', err);
      setError('Error processing resume. Please try again.');
      setResult(null);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="resume-upload-container">
      <h2 className="title">Resume Upload</h2>
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="dropzone">
          <label htmlFor="dropzone-file" className="dropzone-label">
            <Upload className="upload-icon" />
            <p><span className="bold">Click to upload</span> or drag and drop</p>
            <p className="file-types">PDF or Word Document (MAX. 10MB)</p>
          </label>
          <input id="dropzone-file" type="file" className="file-input" onChange={handleFileChange} accept=".pdf,.doc,.docx" />
        </div>
        {file && (
          <div className="file-info">
            <FileText className="file-icon" />
            <span>{file.name}</span>
          </div>
        )}
        <button
          type="submit"
          disabled={!file || isUploading}
          className={`submit-button ${(!file || isUploading) ? 'disabled' : ''}`}
        >
          {isUploading ? 'Processing...' : 'Upload and Extract'}
        </button>
      </form>
      {error && (
        <div className="alert error">
          <AlertCircle className="alert-icon" />
          <p>{error}</p>
        </div>
      )}
      {result && (
        <div className="result-container">
          <div className="result-header">
            <Check className="check-icon" />
            <h3>Extracted Information:</h3>
          </div>
          <pre className="result-content">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;