import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import axios from 'axios';
import ReactFlow, { Background, Controls, MiniMap, Panel } from 'reactflow';
import 'reactflow/dist/style.css';
import './ResearchDashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const ResearchDashboard = () => {
  const [papers, setPapers] = useState([]);
  const [selectedPaper, setSelectedPaper] = useState(null);
  const [title, setTitle] = useState('');
  const [authors, setAuthors] = useState('');
  const [abstract, setAbstract] = useState('');
  const [content, setContent] = useState('');
  const [doi, setDoi] = useState('');
  const [keywords, setKeywords] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [activeTab, setActiveTab] = useState('create'); // 'create', 'search', 'graph'

  useEffect(() => {
    loadPapers();
  }, []);

  useEffect(() => {
    if (selectedPaper) {
      loadPaperGraph(selectedPaper);
    }
  }, [selectedPaper]);

  const loadPapers = async () => {
    try {
      const response = await memoryAPI.searchMemories(
        'research document paper',
        30,
        0.5,
        false
      );
      const researchMemories = response.data.memories || [];
      setPapers(researchMemories);
    } catch (error) {
      console.error('Error loading papers:', error);
    }
  };

  const loadPaperGraph = async (paperId) => {
    try {
      const response = await memoryAPI.getGraphVisualization(100, null, true);
      const graphData = response.data;
      
      const paperNode = graphData.nodes.find(n => n.id === paperId);
      if (paperNode) {
        const relatedNodes = graphData.nodes.filter(
          n => graphData.edges.some(
            e => (e.source === paperId && e.target === n.id) || 
                 (e.target === paperId && e.source === n.id)
          )
        );
        
        const flowNodes = [
          {
            id: paperNode.id,
            type: 'default',
            position: { x: 400, y: 200 },
            data: { label: paperNode.metadata?.title || paperNode.label },
            style: { background: '#ec4899', color: 'white', width: 250 }
          },
          ...relatedNodes.slice(0, 12).map((node, idx) => ({
            id: node.id,
            type: 'default',
            position: {
              x: 100 + (idx % 4) * 200,
              y: 400 + Math.floor(idx / 4) * 150
            },
            data: { label: node.metadata?.title || node.label },
            style: { background: '#fce7f3', width: 200 }
          }))
        ];
        
        const flowEdges = graphData.edges
          .filter(e => e.source === paperId || e.target === paperId)
          .slice(0, 12)
          .map(edge => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: edge.type,
            style: { stroke: '#ec4899', strokeWidth: 2 }
          }));
        
        setNodes(flowNodes);
        setEdges(flowEdges);
      }
    } catch (error) {
      console.error('Error loading graph:', error);
    }
  };

  const createPaper = async () => {
    if (!title.trim() || !abstract.trim() || !content.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/use-cases/research/document`,
        {
          title,
          authors: authors.split(',').map(a => a.trim()).filter(Boolean),
          abstract,
          content,
          doi: doi || null,
          keywords: keywords.split(',').map(k => k.trim()).filter(Boolean),
          publication_date: new Date().toISOString(),
          metadata: {
            created_at: new Date().toISOString()
          }
        }
      );

      setTitle('');
      setAuthors('');
      setAbstract('');
      setContent('');
      setDoi('');
      setKeywords('');
      loadPapers();
      alert('Research paper added successfully!');
    } catch (error) {
      console.error('Error creating paper:', error);
      alert('Failed to add paper');
    } finally {
      setLoading(false);
    }
  };

  const searchPapers = async () => {
    if (!searchQuery.trim()) return;

    try {
      const response = await axios.get(
        `${API_BASE_URL}/use-cases/research/search`,
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
    <div className="research-dashboard">
      <div className="research-header">
        <h1>🔬 Research Tools Platform</h1>
        <p>Build knowledge graphs from research papers, documents, and scholarly articles</p>
      </div>

      <div className="research-layout">
        {/* Papers Sidebar */}
        <div className="papers-sidebar">
          <h2>Research Papers</h2>
          <div className="papers-list">
            {papers.map((paper, idx) => (
              <div
                key={idx}
                className={`paper-item ${selectedPaper === paper.id ? 'active' : ''}`}
                onClick={() => setSelectedPaper(paper.id)}
              >
                <div className="paper-icon">📄</div>
                <div className="paper-info">
                  <div className="paper-title">
                    {paper.metadata?.title || paper.content.substring(0, 40) + '...'}
                  </div>
                  <div className="paper-meta">
                    {paper.metadata?.authors ? paper.metadata.authors.join(', ') : 'Unknown authors'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="research-main">
          <div className="research-tabs">
            <button 
              className={`tab ${activeTab === 'create' ? 'active' : ''}`}
              onClick={() => setActiveTab('create')}
            >
              Add Paper
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

          <div className="research-content">
            {/* Add Paper Tab */}
            {activeTab === 'create' && (
            <div className="add-paper">
              <h2>Add Research Paper</h2>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Paper title"
                />
              </div>
              <div className="form-group">
                <label>Authors (comma-separated)</label>
                <input
                  type="text"
                  value={authors}
                  onChange={(e) => setAuthors(e.target.value)}
                  placeholder="Author 1, Author 2, Author 3"
                />
              </div>
              <div className="form-group">
                <label>DOI</label>
                <input
                  type="text"
                  value={doi}
                  onChange={(e) => setDoi(e.target.value)}
                  placeholder="10.1000/xyz123"
                />
              </div>
              <div className="form-group">
                <label>Abstract</label>
                <textarea
                  value={abstract}
                  onChange={(e) => setAbstract(e.target.value)}
                  placeholder="Paper abstract..."
                  rows="4"
                />
              </div>
              <div className="form-group">
                <label>Full Content</label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Paper content, methodology, results, conclusions..."
                  rows="10"
                />
              </div>
              <div className="form-group">
                <label>Keywords (comma-separated)</label>
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="keyword1, keyword2, keyword3"
                />
              </div>
              <button
                onClick={createPaper}
                disabled={loading || !title.trim() || !abstract.trim() || !content.trim()}
                className="create-btn"
              >
                {loading ? 'Adding...' : 'Add Research Paper'}
              </button>
            </div>
            )}

            {/* Search Tab */}
            {activeTab === 'search' && (
            <div className="search-section">
              <h2>Search Research Papers</h2>
              <div className="search-input-group">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') searchPapers();
                  }}
                  placeholder="Search papers with semantic understanding..."
                  className="search-input"
                />
                <button onClick={searchPapers} className="search-btn">
                  Search
                </button>
              </div>
              {searchResults.length > 0 && (
                <div className="search-results">
                  <h3>Results ({searchResults.length})</h3>
                  {searchResults.map((result, idx) => (
                    <div key={idx} className="result-card">
                      <h4>{result.title}</h4>
                      <div className="result-authors">
                        {result.authors && result.authors.length > 0 && (
                          <span>Authors: {result.authors.join(', ')}</span>
                        )}
                        {result.doi && <span>DOI: {result.doi}</span>}
                      </div>
                      <p className="result-abstract">{result.abstract}</p>
                      <div className="result-meta">
                        <span>Similarity: {(result.similarity * 100).toFixed(1)}%</span>
                        {result.keywords && result.keywords.length > 0 && (
                          <div className="result-keywords">
                            {result.keywords.map((kw, i) => (
                              <span key={i} className="keyword-tag">{kw}</span>
                            ))}
                          </div>
                        )}
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
                {selectedPaper && nodes.length > 0 ? (
              <div className="graph-view" style={{ height: '600px' }}>
                <h2>Research Paper Network</h2>
                <ReactFlow nodes={nodes} edges={edges} fitView>
                  <Background />
                  <Controls />
                  <MiniMap />
                  <Panel position="top-right">Paper Relationships</Panel>
                </ReactFlow>
              </div>
              ) : (
                <div className="no-selection">
                  <p>Please select a research paper from the sidebar to view its citation network.</p>
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

export default ResearchDashboard;

