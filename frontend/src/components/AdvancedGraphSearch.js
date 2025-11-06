import React, { useState } from 'react';
import { memoryAPI } from '../services/api';
import './AdvancedGraphSearch.css';

const AdvancedGraphSearch = () => {
  const [searchType, setSearchType] = useState('path'); // 'path', 'multi-hop', 'community'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  // Path search state
  const [pathSearch, setPathSearch] = useState({
    sourceId: '',
    targetId: '',
    maxHops: 3,
    minConfidence: 0.5,
    relationshipTypes: []
  });

  // Multi-hop search state
  const [multiHopSearch, setMultiHopSearch] = useState({
    query: '',
    startMemoryId: '',
    maxHops: 2,
    limit: 20,
    relationshipTypes: []
  });

  const handlePathSearch = async () => {
    if (!pathSearch.sourceId.trim()) {
      setError('Source memory ID is required');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await memoryAPI.pathSearch(
        pathSearch.sourceId,
        pathSearch.targetId || null,
        pathSearch.maxHops,
        pathSearch.relationshipTypes.length > 0 ? pathSearch.relationshipTypes : null,
        pathSearch.minConfidence
      );
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMultiHopSearch = async () => {
    if (!multiHopSearch.query.trim() && !multiHopSearch.startMemoryId.trim()) {
      setError('Either query or start memory ID is required');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await memoryAPI.multiHopSearch(
        multiHopSearch.query || null,
        multiHopSearch.startMemoryId || null,
        multiHopSearch.maxHops,
        multiHopSearch.limit,
        multiHopSearch.relationshipTypes.length > 0 ? multiHopSearch.relationshipTypes : null
      );
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCommunityDetection = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await memoryAPI.detectCommunities(3);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="advanced-graph-search">
      <h2>Advanced Graph Search</h2>

      <div className="search-type-selector">
        <button
          className={searchType === 'path' ? 'active' : ''}
          onClick={() => setSearchType('path')}
        >
          Path Search
        </button>
        <button
          className={searchType === 'multi-hop' ? 'active' : ''}
          onClick={() => setSearchType('multi-hop')}
        >
          Multi-Hop Search
        </button>
        <button
          className={searchType === 'community' ? 'active' : ''}
          onClick={() => setSearchType('community')}
        >
          Community Detection
        </button>
      </div>

      {searchType === 'path' && (
        <div className="search-panel">
          <h3>Find Path Between Memories</h3>
          <div className="form-group">
            <label>Source Memory ID:</label>
            <input
              type="text"
              value={pathSearch.sourceId}
              onChange={(e) => setPathSearch({...pathSearch, sourceId: e.target.value})}
              placeholder="mem_123..."
            />
          </div>
          <div className="form-group">
            <label>Target Memory ID (optional):</label>
            <input
              type="text"
              value={pathSearch.targetId}
              onChange={(e) => setPathSearch({...pathSearch, targetId: e.target.value})}
              placeholder="mem_456..."
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Max Hops:</label>
              <input
                type="number"
                value={pathSearch.maxHops}
                onChange={(e) => setPathSearch({...pathSearch, maxHops: parseInt(e.target.value)})}
                min="1"
                max="10"
              />
            </div>
            <div className="form-group">
              <label>Min Confidence:</label>
              <input
                type="number"
                step="0.1"
                value={pathSearch.minConfidence}
                onChange={(e) => setPathSearch({...pathSearch, minConfidence: parseFloat(e.target.value)})}
                min="0"
                max="1"
              />
            </div>
          </div>
          <button onClick={handlePathSearch} disabled={loading}>
            {loading ? 'Searching...' : 'Find Path'}
          </button>
        </div>
      )}

      {searchType === 'multi-hop' && (
        <div className="search-panel">
          <h3>Multi-Hop Graph Traversal</h3>
          <div className="form-group">
            <label>Search Query:</label>
            <input
              type="text"
              value={multiHopSearch.query}
              onChange={(e) => setMultiHopSearch({...multiHopSearch, query: e.target.value})}
              placeholder="Enter semantic query..."
            />
          </div>
          <div className="form-group">
            <label>OR Start Memory ID:</label>
            <input
              type="text"
              value={multiHopSearch.startMemoryId}
              onChange={(e) => setMultiHopSearch({...multiHopSearch, startMemoryId: e.target.value})}
              placeholder="mem_123..."
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Max Hops:</label>
              <input
                type="number"
                value={multiHopSearch.maxHops}
                onChange={(e) => setMultiHopSearch({...multiHopSearch, maxHops: parseInt(e.target.value)})}
                min="1"
                max="5"
              />
            </div>
            <div className="form-group">
              <label>Result Limit:</label>
              <input
                type="number"
                value={multiHopSearch.limit}
                onChange={(e) => setMultiHopSearch({...multiHopSearch, limit: parseInt(e.target.value)})}
                min="1"
                max="100"
              />
            </div>
          </div>
          <button onClick={handleMultiHopSearch} disabled={loading}>
            {loading ? 'Searching...' : 'Traverse Graph'}
          </button>
        </div>
      )}

      {searchType === 'community' && (
        <div className="search-panel">
          <h3>Community Detection</h3>
          <p>Detect clusters of related memories in the knowledge graph</p>
          <button onClick={handleCommunityDetection} disabled={loading}>
            {loading ? 'Detecting...' : 'Detect Communities'}
          </button>
        </div>
      )}

      {error && (
        <div className="error-box">
          <strong>Error:</strong> {error}
        </div>
      )}

      {results && (
        <div className="results-panel">
          <h3>Results</h3>
          {searchType === 'path' && results.paths && (
            <div>
              <p>Found {results.total_paths} path(s)</p>
              {results.paths.map((path, idx) => (
                <div key={idx} className="path-result">
                  <h4>Path {idx + 1} (Length: {path.length})</h4>
                  <div className="path-visualization">
                    {path.nodes.map((node, nodeIdx) => (
                      <div key={nodeIdx} className="path-node">
                        <span className="node-id">{node.id}</span>
                        <span className="node-content">{node.content}</span>
                        {nodeIdx < path.nodes.length - 1 && <span className="arrow">→</span>}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {searchType === 'multi-hop' && results.memories && (
            <div>
              <p>Found {results.total_found} memories (Max hops: {results.max_hops})</p>
              <div className="memories-list">
                {results.memories.map((memory) => (
                  <div key={memory.id} className="memory-item">
                    <div className="memory-header">
                      <span className="memory-id">{memory.id}</span>
                      {memory.metadata?.hop_count && (
                        <span className="hop-badge">{memory.metadata.hop_count} hop(s)</span>
                      )}
                    </div>
                    <div className="memory-content">{memory.content}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {searchType === 'community' && results.communities && (
            <div>
              <p>Found {results.total_communities} communities</p>
              {results.communities.map((community, idx) => (
                <div key={idx} className="community-item">
                  <h4>Community {community.community_id || idx + 1} ({community.size || community.degree} memories)</h4>
                  {community.memories && (
                    <ul>
                      {community.memories.map((mem) => (
                        <li key={mem.id}>{mem.id}: {mem.content}</li>
                      ))}
                    </ul>
                  )}
                  {community.content && (
                    <p><strong>{community.memory_id}:</strong> {community.content}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdvancedGraphSearch;

