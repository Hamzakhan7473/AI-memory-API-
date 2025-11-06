import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import './GraphStats.css';

const GraphStats = ({ refreshTrigger }) => {
  const [stats, setStats] = useState(null);
  const [detailedStats, setDetailedStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDetailed, setShowDetailed] = useState(false);

  useEffect(() => {
    loadStats();
  }, [refreshTrigger]);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const [basicResponse, detailedResponse] = await Promise.all([
        memoryAPI.getGraphStats(),
        memoryAPI.getDetailedStats()
      ]);
      setStats(basicResponse.data);
      setDetailedStats(detailedResponse.data);
    } catch (err) {
      setError(err.message || 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading statistics...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!stats) {
    return <div className="loading">No statistics available</div>;
  }

  const relationshipData = [
    { name: 'Update', value: stats.relationships?.update || 0, color: '#dc3545' },
    { name: 'Extend', value: stats.relationships?.extend || 0, color: '#28a745' },
    { name: 'Derive', value: stats.relationships?.derive || 0, color: '#ffc107' },
  ];

  const overviewData = [
    { name: 'Total Memories', value: stats.total_memories },
    { name: 'Latest Memories', value: stats.latest_memories },
    { name: 'Total Relationships', value: stats.relationships?.total || 0 },
  ];

  return (
    <div className="graph-stats">
      <div className="stats-header">
        <h2>Knowledge Graph Statistics</h2>
        <button 
          onClick={() => setShowDetailed(!showDetailed)}
          className="toggle-btn"
        >
          {showDetailed ? 'Show Basic Stats' : 'Show Detailed Stats'}
        </button>
      </div>

      {!showDetailed ? (
        <div className="stats-grid">
          <div className="card">
            <h2>Overview</h2>
            <div className="stats-overview">
              {overviewData.map((item, idx) => (
                <div key={idx} className="stat-card">
                  <div className="stat-value">{item.value}</div>
                  <div className="stat-label">{item.name}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h2>Relationship Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={relationshipData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {relationshipData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h2>Relationship Types</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={relationshipData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#61dafb">
                  {relationshipData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h2>Additional Metrics</h2>
            <div className="metrics-list">
              <div className="metric-item">
                <span className="metric-label">Average Relationships per Memory:</span>
                <span className="metric-value">
                  {stats.average_relationships_per_memory || 0}
                </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Outdated Memories:</span>
                <span className="metric-value">
                  {(stats.total_memories || 0) - (stats.latest_memories || 0)}
                </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Memory Versioning Ratio:</span>
                <span className="metric-value">
                  {stats.total_memories > 0
                    ? ((stats.latest_memories / stats.total_memories) * 100).toFixed(1)
                    : 0}%
                </span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        detailedStats && (
          <div className="detailed-stats">
            <div className="stats-grid">
              <div className="card">
                <h2>Memory Overview</h2>
                <div className="stats-overview">
                  <div className="stat-card">
                    <div className="stat-value">{detailedStats.total_memories}</div>
                    <div className="stat-label">Total Memories</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{detailedStats.latest_memories}</div>
                    <div className="stat-label">Latest</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{detailedStats.outdated_memories}</div>
                    <div className="stat-label">Outdated</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{detailedStats.total_relationships}</div>
                    <div className="stat-label">Relationships</div>
                  </div>
                </div>
              </div>

              {detailedStats.memory_growth && detailedStats.memory_growth.length > 0 && (
                <div className="card">
                  <h2>Memory Growth (Last 30 Days)</h2>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={detailedStats.memory_growth}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="count" stroke="#007bff" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              <div className="card">
                <h2>Source Distribution</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={Object.entries(detailedStats.source_distribution || {}).map(([key, value]) => ({ name: key, value }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#28a745" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="card">
                <h2>Relationship Strength</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={Object.entries(detailedStats.relationship_strength_distribution || {}).map(([key, value]) => ({ name: key, value }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#ffc107" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {detailedStats.top_connected_memories && detailedStats.top_connected_memories.length > 0 && (
                <div className="card">
                  <h2>Top Connected Memories</h2>
                  <div className="top-connected-list">
                    {detailedStats.top_connected_memories.map((mem, idx) => (
                      <div key={idx} className="connected-memory-item">
                        <div className="memory-rank">#{idx + 1}</div>
                        <div className="memory-info">
                          <div className="memory-id">{mem.memory_id}</div>
                          <div className="memory-content">{mem.content}</div>
                        </div>
                        <div className="memory-degree">{mem.degree} connections</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="card">
                <h2>Quality Metrics</h2>
                <div className="metrics-list">
                  <div className="metric-item">
                    <span className="metric-label">Average Confidence:</span>
                    <span className="metric-value">
                      {detailedStats.memory_quality_metrics?.average_confidence || 0}
                    </span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Graph Density:</span>
                    <span className="metric-value">
                      {detailedStats.memory_quality_metrics?.graph_density || 0}
                    </span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Connectivity Ratio:</span>
                    <span className="metric-value">
                      {detailedStats.memory_quality_metrics?.connectivity_ratio || 0}
                    </span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Average Relationships per Memory:</span>
                    <span className="metric-value">
                      {detailedStats.average_relationships_per_memory || 0}
                    </span>
                  </div>
                </div>
              </div>

              {detailedStats.temporal_stats && (
                <div className="card">
                  <h2>Temporal Statistics</h2>
                  <div className="metrics-list">
                    <div className="metric-item">
                      <span className="metric-label">Earliest Memory:</span>
                      <span className="metric-value">
                        {detailedStats.temporal_stats.earliest_memory ? 
                          new Date(detailedStats.temporal_stats.earliest_memory).toLocaleDateString() : 
                          'N/A'}
                      </span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Latest Memory:</span>
                      <span className="metric-value">
                        {detailedStats.temporal_stats.latest_memory ? 
                          new Date(detailedStats.temporal_stats.latest_memory).toLocaleDateString() : 
                          'N/A'}
                      </span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Time Span:</span>
                      <span className="metric-value">
                        {detailedStats.temporal_stats.total_days} days
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )
      )}

      <div className="card">
        <button onClick={loadStats} className="btn-secondary">
          Refresh Statistics
        </button>
      </div>
    </div>
  );
};

export default GraphStats;

