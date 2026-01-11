import React, { useState, useCallback } from 'react';
import { uploadPDFs } from '../api';
import { PDFUploadResult, UploadError } from '../types';

interface FileUploadProps {
  onUploadSuccess: (results: PDFUploadResult[]) => void;
}

export function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadErrors, setUploadErrors] = useState<UploadError[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === 'application/pdf'
    );

    if (files.length > 0) {
      setSelectedFiles((prev) => [...prev, ...files]);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    if (files.length > 0) {
      setSelectedFiles((prev) => [...prev, ...files]);
    }
    // Reset input to allow selecting the same file again
    e.target.value = '';
  }, []);

  const removeFile = useCallback((index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleUpload = useCallback(async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setUploadErrors([]);

    try {
      const response = await uploadPDFs(selectedFiles);
      
      if (response.uploaded.length > 0) {
        onUploadSuccess(response.uploaded);
        setSelectedFiles([]);
      }
      
      if (response.errors.length > 0) {
        setUploadErrors(response.errors);
      }
    } catch (error) {
      setUploadErrors([{ filename: 'Upload', error: 'Failed to upload files. Please try again.' }]);
    } finally {
      setIsUploading(false);
    }
  }, [selectedFiles, onUploadSuccess]);

  return (
    <div className="file-upload">
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="drop-zone-content">
          <svg
            className="upload-icon"
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <p>Drag & drop PDF files here</p>
          <p className="or-text">or</p>
          <label className="file-input-label">
            Browse Files
            <input
              type="file"
              accept=".pdf"
              multiple
              onChange={handleFileSelect}
              className="file-input"
            />
          </label>
        </div>
      </div>

      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <h4>Selected Files ({selectedFiles.length})</h4>
          <ul>
            {selectedFiles.map((file, index) => (
              <li key={`${file.name}-${index}`}>
                <span className="file-name">{file.name}</span>
                <span className="file-size">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
                <button
                  className="remove-file"
                  onClick={() => removeFile(index)}
                  type="button"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
          <button
            className="upload-button"
            onClick={handleUpload}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Upload PDFs'}
          </button>
        </div>
      )}

      {uploadErrors.length > 0 && (
        <div className="upload-errors">
          <h4>Upload Errors</h4>
          <ul>
            {uploadErrors.map((error, index) => (
              <li key={index}>
                <strong>{error.filename}:</strong> {error.error}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
