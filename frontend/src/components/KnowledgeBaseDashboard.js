import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import axios from 'axios';
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';
import './KnowledgeBaseDashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const KnowledgeBaseDashboard = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadCategory, setUploadCategory] = useState('');
  const [uploadTags, setUploadTags] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [createMode, setCreateMode] = useState('manual'); // 'manual' or 'upload'
  const [activeTab, setActiveTab] = useState('create'); // 'create', 'search', 'graph'

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    if (selectedDoc) {
      loadDocumentGraph(selectedDoc);
    }
  }, [selectedDoc]);

  const loadDocuments = async () => {
    try {
      // Use the dedicated list endpoint to get all knowledge base documents
      const response = await axios.get(
        `${API_BASE_URL}/use-cases/knowledge-base/list`,
        {
          params: {
            limit: 50,
            offset: 0
          }
        }
      );
      const kbDocuments = response.data.documents || [];
      setDocuments(kbDocuments);
    } catch (error) {
      console.error('Error loading documents:', error);
      // Fallback to search if list endpoint fails
      try {
        const searchResponse = await memoryAPI.searchMemories(
          'knowledge base document',
          50,
          0.3,
          false
        );
        const kbMemories = searchResponse.data.memories || [];
        setDocuments(kbMemories);
      } catch (searchError) {
        console.error('Error with fallback search:', searchError);
      }
    }
  };

  const loadDocumentGraph = async (docId) => {
    try {
      // Find the document to get its source_id
      const doc = documents.find(d => d.id === docId || d.source_id === docId);
      if (!doc) return;
      
      const sourceId = doc.source_id || docId;
      
      // Get all memories for this document (by source_id)
      // Use API endpoint to get document graph
      try {
        const graphResponse = await axios.get(
          `${API_BASE_URL}/use-cases/knowledge-base/graph/${encodeURIComponent(sourceId)}`
        );
        const graphData = graphResponse.data;
        
        // Build React Flow nodes from graph data
        const flowNodes = graphData.nodes.map((node, idx) => ({
          id: node.id,
          type: 'default',
          position: {
            x: 250 + (idx % 4) * 200,
            y: 100 + Math.floor(idx / 4) * 150
          },
          data: { label: node.label || node.content?.substring(0, 30) + '...' },
          style: idx === 0 ? { background: '#3b82f6', color: 'white', width: 200 } : { background: '#e5e7eb', width: 180 }
        }));
        
        const flowEdges = graphData.edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.type,
          style: { stroke: '#3b82f6', strokeWidth: 2 }
        }));
        
        setNodes(flowNodes);
        setEdges(flowEdges);
      } catch (apiError) {
        // Fallback to graph visualization
        console.log('Using fallback graph visualization');
        const response = await memoryAPI.getGraphVisualization(100, null, true);
        const graphData = response.data;
        
        // Filter nodes related to this document
        const docNodes = graphData.nodes.filter(n => n.id === docId || n.metadata?.source_id === sourceId);
        if (docNodes.length > 0) {
          const relatedNodes = graphData.nodes.filter(
            n => graphData.edges.some(
              e => docNodes.some(dn => (dn.id === e.source && n.id === e.target) || 
                                      (dn.id === e.target && n.id === e.source))
            )
          );
          
          const flowNodes = docNodes.map((node, idx) => ({
            id: node.id,
            type: 'default',
            position: { x: 250, y: 100 + idx * 150 },
            data: { label: node.label },
            style: { background: '#3b82f6', color: 'white', width: 200 }
          })).concat(relatedNodes.slice(0, 10).map((node, idx) => ({
            id: node.id,
            type: 'default',
            position: { x: 500, y: 100 + idx * 150 },
            data: { label: node.label },
            style: { background: '#e5e7eb', width: 180 }
          })));
          
          const flowEdges = graphData.edges
            .filter(e => docNodes.some(dn => dn.id === e.source || dn.id === e.target))
            .slice(0, 10)
            .map(edge => ({
              id: edge.id,
              source: edge.source,
              target: edge.target,
              label: edge.type,
              style: { stroke: '#3b82f6', strokeWidth: 2 }
            }));
          
          setNodes(flowNodes);
          setEdges(flowEdges);
        }
      }
    } catch (error) {
      console.error('Error loading graph:', error);
      // Fallback to basic graph visualization
      try {
        // Find the document to get its source_id
        const doc = documents.find(d => d.id === docId || d.source_id === docId);
        const sourceId = doc?.source_id || docId;
        
        const response = await memoryAPI.getGraphVisualization(100, null, true);
        const graphData = response.data;
        const docNodes = graphData.nodes.filter(n => n.id === docId || n.metadata?.source_id === sourceId);
        if (docNodes.length > 0) {
          const relatedNodes = graphData.nodes.filter(
            n => graphData.edges.some(
              e => docNodes.some(dn => dn.id === e.source && n.id === e.target) ||
                   docNodes.some(dn => dn.id === e.target && n.id === e.source)
            )
          );
          
          const flowNodes = docNodes.map((node, idx) => ({
            id: node.id,
            type: 'default',
            position: { x: 250, y: 100 + idx * 150 },
            data: { label: node.label },
            style: { background: '#3b82f6', color: 'white', width: 200 }
          })).concat(relatedNodes.slice(0, 10).map((node, idx) => ({
            id: node.id,
            type: 'default',
            position: { x: 500, y: 100 + idx * 150 },
            data: { label: node.label },
            style: { background: '#e5e7eb', width: 180 }
          })));
          
          const flowEdges = graphData.edges
            .filter(e => docNodes.some(dn => dn.id === e.source || dn.id === e.target))
            .slice(0, 10)
            .map(edge => ({
              id: edge.id,
              source: edge.source,
              target: edge.target,
              label: edge.type,
              style: { stroke: '#3b82f6', strokeWidth: 2 }
            }));
          
          setNodes(flowNodes);
          setEdges(flowEdges);
        }
      } catch (fallbackError) {
        console.error('Error with fallback graph:', fallbackError);
      }
    }
  };

  const createDocument = async () => {
    if (!title.trim() || !content.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/use-cases/knowledge-base/document`,
        {
          title,
          content,
          category: category || null,
          tags: tags.split(',').map(t => t.trim()).filter(Boolean),
          metadata: {
            created_at: new Date().toISOString()
          }
        }
      );

      setTitle('');
      setContent('');
      setCategory('');
      setTags('');
      loadDocuments();
      alert('Document created successfully!');
    } catch (error) {
      console.error('Error creating document:', error);
      alert('Failed to create document');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const ext = file.name.split('.').pop().toLowerCase();
      if (['pdf', 'docx', 'doc'].includes(ext)) {
        setSelectedFile(file);
      } else {
        alert('Please select a PDF or Word document (.pdf, .docx, .doc)');
        e.target.value = '';
      }
    }
  };

  const uploadDocument = async () => {
    if (!selectedFile) {
      alert('Please select a file to upload');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (uploadCategory) formData.append('category', uploadCategory);
      if (uploadTags) formData.append('tags', uploadTags);

      const response = await axios.post(
        `${API_BASE_URL}/use-cases/knowledge-base/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setSelectedFile(null);
      setUploadCategory('');
      setUploadTags('');
      document.getElementById('file-input').value = '';
      loadDocuments();
      alert(`Document uploaded successfully! Created ${response.data.memories_created} memories from ${response.data.total_chunks} chunks.`);
    } catch (error) {
      console.error('Error uploading document:', error);
      alert(`Failed to upload document: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const searchDocuments = async () => {
    if (!searchQuery.trim()) return;

    try {
      const response = await axios.get(
        `${API_BASE_URL}/use-cases/knowledge-base/search`,
        {
          params: {
            query: searchQuery,
            limit: 10
          }
        }
      );
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Error searching:', error);
    }
  };

  return (
    <div className="knowledge-base-dashboard">
      <div className="kb-header">
        <h1>📚 Knowledge Base Platform</h1>
        <p>Transform documents into searchable knowledge graphs with semantic understanding</p>
      </div>

      <div className="kb-layout">
        {/* Documents Sidebar */}
        <div className="documents-sidebar">
          <h2>Documents</h2>
          <div className="documents-list">
            {documents.map((doc, idx) => (
              <div
                key={doc.source_id || doc.id || idx}
                className={`document-item ${selectedDoc === doc.id || selectedDoc === doc.source_id ? 'active' : ''}`}
                onClick={() => setSelectedDoc(doc.id)}
              >
                <div className="doc-icon">📄</div>
                <div className="doc-info">
                  <div className="doc-title">
                    {doc.title || doc.metadata?.title || doc.filename || doc.content?.substring(0, 40) + '...'}
                  </div>
                  <div className="doc-meta">
                    <span>{doc.category || doc.metadata?.category || 'Uncategorized'}</span>
                    {doc.chunk_count && <span className="chunk-count">({doc.chunk_count} chunks)</span>}
                    {doc.file_type && <span className="file-type">{doc.file_type.toUpperCase()}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="kb-main">
          <div className="kb-tabs">
            <button 
              className={`tab ${activeTab === 'create' ? 'active' : ''}`}
              onClick={() => setActiveTab('create')}
            >
              Create Document
            </button>
            <button 
              className={`tab ${activeTab === 'search' ? 'active' : ''}`}
              onClick={() => setActiveTab('search')}
            >
              Search
            </button>
            <button 
              className={`tab ${activeTab === 'graph' ? 'active' : ''}`}
              onClick={() => setActiveTab('graph')}
            >
              Graph View
            </button>
          </div>

          <div className="kb-content">
            {/* Create Document Tab */}
            {activeTab === 'create' && (
            <div className="create-document">
              <h2>Create New Document</h2>
              <div className="upload-tabs">
                <button 
                  className={`tab-btn ${createMode === 'manual' ? 'active' : ''}`}
                  onClick={() => setCreateMode('manual')}
                >
                  Manual Entry
                </button>
                <button 
                  className={`tab-btn ${createMode === 'upload' ? 'active' : ''}`}
                  onClick={() => setCreateMode('upload')}
                >
                  Upload File (PDF/Word)
                </button>
              </div>
              
              {createMode === 'manual' ? (
              <>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Document title"
                />
              </div>
              <div className="form-group">
                <label>Content</label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Document content..."
                  rows="10"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Category</label>
                  <input
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    placeholder="e.g., Technology, Science"
                  />
                </div>
                <div className="form-group">
                  <label>Tags (comma-separated)</label>
                  <input
                    type="text"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
              </div>
              <button
                onClick={createDocument}
                disabled={loading || !title.trim() || !content.trim()}
                className="create-btn"
              >
                {loading ? 'Creating...' : 'Create Document'}
              </button>
              </>
              ) : (
              <div className="upload-document">
                <h3>Upload Document (PDF or Word)</h3>
                <div className="file-upload-section">
                  <input
                    type="file"
                    id="file-input"
                    accept=".pdf,.docx,.doc"
                    onChange={handleFileSelect}
                    className="file-input"
                  />
                  {selectedFile && (
                    <div className="file-info">
                      <p>Selected: <strong>{selectedFile.name}</strong></p>
                      <p>Size: {(selectedFile.size / 1024).toFixed(2)} KB</p>
                    </div>
                  )}
                </div>
                <div className="form-group">
                  <label>Category (optional)</label>
                  <input
                    type="text"
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value)}
                    placeholder="e.g., Technology, Science"
                  />
                </div>
                <div className="form-group">
                  <label>Tags (optional, comma-separated)</label>
                  <input
                    type="text"
                    value={uploadTags}
                    onChange={(e) => setUploadTags(e.target.value)}
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
                <button
                  onClick={uploadDocument}
                  disabled={uploading || !selectedFile}
                  className="create-btn"
                >
                  {uploading ? 'Uploading...' : 'Upload Document'}
                </button>
              </div>
              )}
            </div>
            )}

            {/* Search Tab */}
            {activeTab === 'search' && (
            <div className="search-section">
              <h2>Search Knowledge Base</h2>
              <div className="search-input-group">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') searchDocuments();
                  }}
                  placeholder="Search with semantic understanding..."
                  className="search-input"
                />
                <button onClick={searchDocuments} className="search-btn">
                  Search
                </button>
              </div>
              {searchResults.length > 0 && (
                <div className="search-results">
                  <h3>Results ({searchResults.length})</h3>
                  {searchResults.map((result, idx) => (
                    <div key={idx} className="result-card">
                      <h4>{result.title}</h4>
                      <p>{result.content}</p>
                      <div className="result-meta">
                        <span>Similarity: {(result.similarity * 100).toFixed(1)}%</span>
                        {result.category && <span>Category: {result.category}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            )}

            {/* Graph View Tab */}
            {activeTab === 'graph' && (
              <div className="graph-view-section">
                {selectedDoc ? (
              <div className="graph-view" style={{ height: '600px' }}>
                <h2>Knowledge Graph</h2>
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  onInit={setReactFlowInstance}
                  fitView
                >
                  <Background />
                  <Controls />
                  <MiniMap />
                </ReactFlow>
              </div>
              ) : (
                <div className="no-selection">
                  <p>Please select a document from the sidebar to view its knowledge graph.</p>
                </div>
              )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBaseDashboard;

