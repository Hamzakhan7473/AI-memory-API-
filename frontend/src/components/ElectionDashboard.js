import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import './ElectionDashboard.css';

const ElectionDashboard = () => {
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [statements, setStatements] = useState([]);
  const [newStatement, setNewStatement] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadCandidates();
    loadStats();
  }, []);

  useEffect(() => {
    if (selectedCandidate) {
      loadStatements(selectedCandidate);
    }
  }, [selectedCandidate, filter]);

  const loadCandidates = async () => {
    try {
      const response = await memoryAPI.searchMemories(
        'NYC mayoral candidate election',
        20,
        0.5,
        false
      );
      const candidateMemories = response.data.memories || [];
      setCandidates(candidateMemories);
    } catch (error) {
      console.error('Error loading candidates:', error);
    }
  };

  const loadStatements = async (candidateId) => {
    try {
      let query = `candidate ${candidateId}`;
      if (filter === 'promises') query += ' promise';
      if (filter === 'policies') query += ' policy';
      
      const response = await memoryAPI.searchMemories(
        query,
        20,
        0.5,
        true
      );
      setStatements(response.data.memories || []);
    } catch (error) {
      console.error('Error loading statements:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await memoryAPI.getGraphStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const createStatement = async () => {
    if (!newStatement.trim() || !selectedCandidate) return;

    setLoading(true);
    try {
      const memoryData = {
        content: newStatement,
        source_type: 'speech',
        source_id: `statement_${Date.now()}`,
        metadata: {
          candidate_id: selectedCandidate,
          date: new Date().toISOString(),
          type: 'campaign_statement',
          event_type: 'campaign_rally',
          verifiable: true
        }
      };

      await memoryAPI.createMemory(memoryData);
      setNewStatement('');
      loadStatements(selectedCandidate);
      loadStats();
    } catch (error) {
      console.error('Error creating statement:', error);
      alert('Failed to create statement');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="election-dashboard">
      <div className="election-header">
        <h1>🗳️ NYC Mayoral Election Platform</h1>
        <p>Track candidates, policy positions, and campaign promises</p>
      </div>

      <div className="election-layout">
        {/* Candidate Sidebar */}
        <div className="candidate-sidebar">
          <h2>Candidates</h2>
          <div className="candidate-list">
            {candidates.map((candidate, idx) => (
              <div
                key={idx}
                className={`candidate-item ${selectedCandidate === candidate.id ? 'active' : ''}`}
                onClick={() => setSelectedCandidate(candidate.id)}
              >
                <div className="candidate-icon">👤</div>
                <div className="candidate-info">
                  <div className="candidate-name">
                    {candidate.metadata?.candidate_name || `Candidate ${candidate.id.slice(-6)}`}
                  </div>
                  <div className="candidate-meta">
                    {candidate.metadata?.party || 'Independent'}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button className="add-candidate-btn">+ Add New Candidate</button>
        </div>

        {/* Main Content */}
        <div className="election-main">
          {selectedCandidate ? (
            <>
              <div className="statement-header">
                <h2>Campaign Statements</h2>
                <div className="statement-filters">
                  <button
                    className={filter === 'all' ? 'active' : ''}
                    onClick={() => setFilter('all')}
                  >
                    All
                  </button>
                  <button
                    className={filter === 'promises' ? 'active' : ''}
                    onClick={() => setFilter('promises')}
                  >
                    Promises
                  </button>
                  <button
                    className={filter === 'policies' ? 'active' : ''}
                    onClick={() => setFilter('policies')}
                  >
                    Policies
                  </button>
                </div>
              </div>

              <div className="statement-stats">
                <div className="stat-item">
                  <span className="stat-label">Total Statements:</span>
                  <span className="stat-value">{statements.length}</span>
                </div>
              </div>

              <div className="new-statement">
                <textarea
                  value={newStatement}
                  onChange={(e) => setNewStatement(e.target.value)}
                  placeholder="Enter campaign statement, policy position, promise, or speech excerpt..."
                  rows="4"
                />
                <button
                  onClick={createStatement}
                  disabled={loading || !newStatement.trim()}
                  className="create-btn"
                >
                  {loading ? 'Creating...' : 'Create Statement'}
                </button>
              </div>

              <div className="statements-list">
                <h3>Statement History</h3>
                {statements.length === 0 ? (
                  <div className="empty-state">
                    <p>No statements found. Create your first statement above.</p>
                  </div>
                ) : (
                  statements.map((statement, idx) => (
                    <div key={idx} className="statement-card">
                      <div className="statement-header">
                        <div className="statement-date">
                          {new Date(statement.metadata?.date || statement.created_at).toLocaleDateString()}
                        </div>
                        <div className="statement-verifiable">
                          {statement.metadata?.verifiable ? '✅ Verifiable' : '⚠️ Not Verified'}
                        </div>
                      </div>
                      <div className="statement-content">{statement.content}</div>
                      {statement.metadata?.topic && (
                        <div className="statement-tags">
                          <span className="tag topic-tag">
                            {statement.metadata.topic}
                          </span>
                          {statement.metadata?.borough && (
                            <span className="tag borough-tag">
                              {statement.metadata.borough}
                            </span>
                          )}
                        </div>
                      )}
                      {statement.metadata?.promise_type && (
                        <div className="promise-type">
                          <strong>Type:</strong> {statement.metadata.promise_type}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <div className="empty-state-large">
              <div className="empty-icon">🗳️</div>
              <h2>Select a Candidate</h2>
              <p>Choose a candidate from the sidebar to view their campaign statements</p>
            </div>
          )}
        </div>

        {/* Stats Sidebar */}
        <div className="stats-sidebar">
          <h2>Statistics</h2>
          {stats && (
            <div className="stats-content">
              <div className="stat-card">
                <div className="stat-icon">📊</div>
                <div className="stat-value">{stats.total_memories || 0}</div>
                <div className="stat-label">Total Statements</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🔗</div>
                <div className="stat-value">{stats.relationships?.total || 0}</div>
                <div className="stat-label">Relationships</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ElectionDashboard;

