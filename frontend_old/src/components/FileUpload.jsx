import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setMessage('');
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    setIsLoading(true);
    setMessage(`Uploading ${file.name}...`);

    try {
      const response = await axios.post('http://127.0.0.1:8000/ingest', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage(response.data.message);
    } catch (error) {
      setMessage('Error uploading file.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <h2>1. Upload Textbook</h2>
      <p>Upload a PDF or TXT file to begin.</p>
      <input type="file" onChange={handleFileChange} accept=".pdf,.txt" />
      <button onClick={handleUpload} disabled={isLoading || !file}>
        {isLoading ? 'Uploading...' : 'Upload'}
      </button>
      {message && <p className="status-message">{message}</p>}
    </div>
  );
};

export default FileUpload;