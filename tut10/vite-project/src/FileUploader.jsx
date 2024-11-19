import React, { useState } from 'react';
import './FileUploadDownload.css';

function FileUploadDownload() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      handleFileUpload(droppedFile);
    }
    setIsDragOver(false);
  };

  const handleFileUpload = async (uploadedFile) => {
    setError("");
    setLoading(true);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await fetch('http://localhost:3000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('File processing failed.');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = 'OutputFile.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error('Error:', err);
      setError('An error occurred while processing the file.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <h1 className="title">IIT Patna Grader</h1>
      <h2 className="subtitle">Upload the input File</h2>

      <div
        className={`file-dropzone ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleFileDrop}
        onClick={() => document.getElementById('fileInput').click()}
      >
        <img
          src="https://w7.pngwing.com/pngs/613/263/png-transparent-computer-icons-dropbox-logo-box-angle-flag-rectangle.png"
          alt="Dropbox Logo"
          style={{ width: '50px', height: 'auto' }}
          className="dropbox-logo"
        />
        <p>{file ? file.name : "Drag & Drop your file here or Click to Upload"}</p>
        <input
          type="file"
          id="fileInput"
          onChange={(e) => handleFileUpload(e.target.files[0])}
          accept=".xlsx"
          className="file-input"
          hidden
        />
      </div>

      {loading && <p className="loading-text">Processing your file, please wait...</p>}
      {error.length > 0 && <div className="error-message">{error}</div>}
      <h2 className="bottom-right">Kushal Agarwal</h2>
    </div>
  );
}

export default FileUploadDownload;
