import React, { useState } from 'react';
import { memoryAPI } from '../services/api';
import './MemorySearch.css';

const MemorySearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    limit: 10,
    minSimilarity: 0.7,
    includeSubgraph: true,
  });

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await memoryAPI.searchMemories(
        query,
        filters.limit,
        filters.minSimilarity,
        filters.includeSubgraph
      );
      setResults(response.data);
    } catch (err) {
      setError(err.message || 'Search failed');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="memory-search">
      <div className="card">
        <h2>Semantic Search</h2>
        <form onSubmit={handleSearch}>
          <div className="form-group">
            <label>Search Query:</label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your search query..."
              rows={3}
            />
          </div>

          <div className="search-filters">
            <div className="form-group">
              <label>Results Limit:</label>
              <input
                type="number"
                value={filters.limit}
                onChange={(e) => setFilters(prev => ({ ...prev, limit: parseInt(e.target.value) }))}
                min="1"
                max="100"
              />
            </div>

            <div className="form-group">
              <label>Min Similarity:</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={filters.minSimilarity}
                onChange={(e) => setFilters(prev => ({ ...prev, minSimilarity: parseFloat(e.target.value) }))}
              />
            </div>

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={filters.includeSubgraph}
                  onChange={(e) => setFilters(prev => ({ ...prev, includeSubgraph: e.target.checked }))}
                />
                {' '}Include Subgraph
              </label>
            </div>
          </div>

          <button type="submit" disabled={loading || !query.trim()}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {error && <div className="error">{error}</div>}

      {results && (
        <div className="search-results">
          <div className="card">
            <h3>Search Results</h3>
            <div className="search-meta">
              <span>Found {results.memories.length} memories</span>
              {results.search_time_ms && (
                <span>Search time: {results.search_time_ms.toFixed(2)}ms</span>
              )}
            </div>

            {results.memories.length === 0 ? (
              <p>No memories found matching your query.</p>
            ) : (
              <div className="results-list">
                {results.memories.map((memory) => (
                  <div key={memory.id} className="result-item">
                    <div className="result-header">
                      <span className="result-id">{memory.id}</span>
                      {memory.metadata?.search_similarity && (
                        <span className="similarity-badge">
                          {(memory.metadata.search_similarity * 100).toFixed(1)}% similar
                        </span>
                      )}
                    </div>
                    <div className="result-content">{memory.content}</div>
                    <div className="result-meta">
                      <span>Created: {new Date(memory.created_at).toLocaleString()}</span>
                      {memory.source_type && <span>Source: {memory.source_type}</span>}
                      {memory.is_latest ? (
                        <span className="badge-success">Latest</span>
                      ) : (
                        <span className="badge-outdated">Outdated</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {results.relationships && results.relationships.length > 0 && (
            <div className="card">
              <h3>Related Relationships ({results.relationships.length})</h3>
              <div className="relationships-list">
                {results.relationships.map((rel) => (
                  <div key={rel.id} className="relationship-item">
                    <span className="relationship-type">{rel.type}</span>
                    <span className="relationship-link">
                      {rel.source_id} → {rel.target_id}
                    </span>
                    <span className="relationship-confidence">
                      {(rel.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MemorySearch;

