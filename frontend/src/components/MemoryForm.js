import React, { useState } from 'react';
import { memoryAPI } from '../services/api';
import './MemoryForm.css';

const MemoryForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    content: '',
    sourceType: 'text',
    metadata: '',
  });
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (formData.sourceType === 'pdf' && pdfFile) {
        // Handle PDF upload
        const response = await memoryAPI.uploadPDF(pdfFile, 1000, 200);
        setSuccess(`Successfully created ${response.data.length} memories from PDF`);
        setFormData({ content: '', sourceType: 'text', metadata: '' });
        setPdfFile(null);
        if (onSuccess) onSuccess();
      } else if (formData.content.trim()) {
        // Handle text input
        const metadata = formData.metadata
          ? JSON.parse(formData.metadata)
          : null;

        const response = await memoryAPI.createMemory({
          content: formData.content,
          source_type: formData.sourceType,
          metadata: metadata,
        });
        setSuccess(`Memory created successfully: ${response.data.id}`);
        setFormData({ content: '', sourceType: 'text', metadata: '' });
        if (onSuccess) onSuccess();
      } else {
        setError('Please provide content or upload a PDF');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to create memory');
      console.error('Error creating memory:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setPdfFile(file);
    } else {
      setError('Please select a valid PDF file');
    }
  };

  return (
    <div className="memory-form">
      <div className="card">
        <h2>Add New Memory</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Source Type:</label>
            <select
              value={formData.sourceType}
              onChange={(e) => setFormData({ ...formData, sourceType: e.target.value })}
            >
              <option value="text">Text</option>
              <option value="pdf">PDF</option>
            </select>
          </div>

          {formData.sourceType === 'text' ? (
            <>
              <div className="form-group">
                <label>Content:</label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  placeholder="Enter memory content..."
                  rows={6}
                  required
                />
              </div>

              <div className="form-group">
                <label>Metadata (JSON, optional):</label>
                <textarea
                  value={formData.metadata}
                  onChange={(e) => setFormData({ ...formData, metadata: e.target.value })}
                  placeholder='{"key": "value"}'
                  rows={3}
                />
              </div>
            </>
          ) : (
            <div className="form-group">
              <label>PDF File:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                required
              />
              {pdfFile && (
                <div className="file-info">
                  Selected: {pdfFile.name} ({(pdfFile.size / 1024).toFixed(2)} KB)
                </div>
              )}
            </div>
          )}

          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}

          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Memory'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default MemoryForm;

