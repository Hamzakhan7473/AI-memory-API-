import React from 'react';
import './MemoryDetails.css';

// Simple JSON viewer component (fallback if react-json-view not available)
const JSONViewer = ({ src }) => {
  return (
    <pre style={{
      background: '#1e1e1e',
      color: '#d4d4d4',
      padding: '15px',
      borderRadius: '4px',
      overflow: 'auto',
      fontSize: '12px',
      maxHeight: '300px'
    }}>
      {JSON.stringify(src, null, 2)}
    </pre>
  );
};

const MemoryDetails = ({ memory, onClose }) => {
  if (!memory || !memory.memory) return null;

  const mem = memory.memory;

  return (
    <div className="memory-details-overlay">
      <div className="memory-details-panel">
        <div className="memory-details-header">
          <h2>Memory Details</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>

        <div className="memory-details-content">
          <div className="detail-section">
            <label>ID:</label>
            <div className="detail-value">{mem.id}</div>
          </div>

          <div className="detail-section">
            <label>Content:</label>
            <div className="detail-value content-box">{mem.content}</div>
          </div>

          <div className="detail-section">
            <label>Source Type:</label>
            <div className="detail-value">{mem.source_type}</div>
          </div>

          {mem.source_id && (
            <div className="detail-section">
              <label>Source ID:</label>
              <div className="detail-value">{mem.source_id}</div>
            </div>
          )}

          <div className="detail-section">
            <label>Created At:</label>
            <div className="detail-value">
              {new Date(mem.created_at).toLocaleString()}
            </div>
          </div>

          <div className="detail-section">
            <label>Updated At:</label>
            <div className="detail-value">
              {new Date(mem.updated_at).toLocaleString()}
            </div>
          </div>

          <div className="detail-section">
            <label>Version:</label>
            <div className="detail-value">{mem.version}</div>
          </div>

          <div className="detail-section">
            <label>Is Latest:</label>
            <div className="detail-value">
              <span className={mem.is_latest ? 'badge-success' : 'badge-outdated'}>
                {mem.is_latest ? 'Yes' : 'No'}
              </span>
            </div>
          </div>

          {mem.metadata && Object.keys(mem.metadata).length > 0 && (
            <div className="detail-section">
              <label>Metadata:</label>
              <div className="detail-value">
                <JSONViewer src={mem.metadata} />
              </div>
            </div>
          )}

          {mem.embedding_dimension && (
            <div className="detail-section">
              <label>Embedding Dimension:</label>
              <div className="detail-value">{mem.embedding_dimension}</div>
            </div>
          )}

          {memory.related_memories && memory.related_memories.length > 0 && (
            <div className="detail-section">
              <label>Related Memories ({memory.related_memories.length}):</label>
              <div className="related-memories">
                {memory.related_memories.map((related, idx) => (
                  <div key={idx} className="related-memory-item">
                    <strong>{related.id}:</strong> {related.content.substring(0, 100)}...
                  </div>
                ))}
              </div>
            </div>
          )}

          {memory.lineage && memory.lineage.length > 1 && (
            <div className="detail-section">
              <label>Version Lineage:</label>
              <div className="lineage">
                {memory.lineage.map((version, idx) => (
                  <div key={idx} className="lineage-item">
                    <div className="lineage-version">v{version.version}</div>
                    <div className="lineage-content">
                      {version.content.substring(0, 150)}...
                    </div>
                    <div className="lineage-date">
                      {new Date(version.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MemoryDetails;

