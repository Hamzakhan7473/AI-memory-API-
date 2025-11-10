import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import './FinanceDashboard.css';

const FinanceDashboard = () => {
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [meetings, setMeetings] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadClients();
    loadStats();
  }, []);

  useEffect(() => {
    if (selectedClient) {
      loadMeetings(selectedClient);
    }
  }, [selectedClient]);

  const loadClients = async () => {
    try {
      const response = await memoryAPI.searchMemories(
        'financial client portfolio advisor',
        20,
        0.5,
        false
      );
      const clientMemories = response.data.memories || [];
      setClients(clientMemories);
    } catch (error) {
      console.error('Error loading clients:', error);
    }
  };

  const loadMeetings = async (clientId) => {
    try {
      const response = await memoryAPI.searchMemories(
        `client ${clientId} meeting portfolio`,
        20,
        0.5,
        true
      );
      setMeetings(response.data.memories || []);
    } catch (error) {
      console.error('Error loading meetings:', error);
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

  const createMeeting = async () => {
    if (!newNote.trim() || !selectedClient) return;

    setLoading(true);
    try {
      const memoryData = {
        content: newNote,
        source_type: 'meeting',
        source_id: `meeting_${Date.now()}`,
        metadata: {
          client_id: selectedClient,
          date: new Date().toISOString(),
          type: 'financial_meeting',
          advisor: 'John Financial Advisor'
        }
      };

      await memoryAPI.createMemory(memoryData);
      setNewNote('');
      loadMeetings(selectedClient);
      loadStats();
    } catch (error) {
      console.error('Error creating meeting:', error);
      alert('Failed to create meeting note');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="finance-dashboard">
      <div className="finance-header">
        <h1>💰 Financial Advisory Platform</h1>
        <p>Manage client portfolios, market insights, and investment strategies</p>
      </div>

      <div className="finance-layout">
        {/* Client Sidebar */}
        <div className="client-sidebar">
          <h2>Clients</h2>
          <div className="client-list">
            {clients.map((client, idx) => (
              <div
                key={idx}
                className={`client-item ${selectedClient === client.id ? 'active' : ''}`}
                onClick={() => setSelectedClient(client.id)}
              >
                <div className="client-icon">💼</div>
                <div className="client-info">
                  <div className="client-name">
                    {client.metadata?.client_name || `Client ${client.id.slice(-6)}`}
                  </div>
                  <div className="client-meta">
                    {client.metadata?.portfolio_value ? 
                      `$${parseInt(client.metadata.portfolio_value).toLocaleString()}` : 
                      'No portfolio info'}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button className="add-client-btn">+ Add New Client</button>
        </div>

        {/* Main Content */}
        <div className="finance-main">
          {selectedClient ? (
            <>
              <div className="meeting-header">
                <h2>Meeting Notes</h2>
                <div className="meeting-stats">
                  <div className="stat-item">
                    <span className="stat-label">Total Meetings:</span>
                    <span className="stat-value">{meetings.length}</span>
                  </div>
                </div>
              </div>

              <div className="new-meeting">
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Enter meeting notes, portfolio changes, market insights, investment strategies..."
                  rows="4"
                />
                <button
                  onClick={createMeeting}
                  disabled={loading || !newNote.trim()}
                  className="create-btn"
                >
                  {loading ? 'Creating...' : 'Create Meeting Note'}
                </button>
              </div>

              <div className="meetings-list">
                <h3>Meeting History</h3>
                {meetings.length === 0 ? (
                  <div className="empty-state">
                    <p>No meeting notes found. Create your first note above.</p>
                  </div>
                ) : (
                  meetings.map((meeting, idx) => (
                    <div key={idx} className="meeting-card">
                      <div className="meeting-header">
                        <div className="meeting-date">
                          {new Date(meeting.metadata?.date || meeting.created_at).toLocaleDateString()}
                        </div>
                        <div className="meeting-advisor">
                          {meeting.metadata?.advisor || 'Advisor Unknown'}
                        </div>
                      </div>
                      <div className="meeting-content">{meeting.content}</div>
                      {meeting.metadata?.asset_class && (
                        <div className="meeting-tags">
                          <span className="tag asset-tag">
                            {meeting.metadata.asset_class}
                          </span>
                          {meeting.metadata?.sector && (
                            <span className="tag sector-tag">
                              {meeting.metadata.sector}
                            </span>
                          )}
                        </div>
                      )}
                      {meeting.metadata?.risk_level && (
                        <div className="risk-level">
                          <strong>Risk Level:</strong> {meeting.metadata.risk_level}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <div className="empty-state-large">
              <div className="empty-icon">💰</div>
              <h2>Select a Client</h2>
              <p>Choose a client from the sidebar to view their meeting history</p>
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
                <div className="stat-label">Total Records</div>
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

export default FinanceDashboard;

