import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './GraphStats.css';

const GraphStats = ({ refreshTrigger }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStats();
  }, [refreshTrigger]);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await memoryAPI.getGraphStats();
      setStats(response.data);
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

      <div className="card">
        <button onClick={loadStats} className="btn-secondary">
          Refresh Statistics
        </button>
      </div>
    </div>
  );
};

export default GraphStats;

