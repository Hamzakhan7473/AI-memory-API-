import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import axios from 'axios';
import './SupportDashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const SupportDashboard = () => {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [profile, setProfile] = useState(null);
  const [interactionType, setInteractionType] = useState('chat');
  const [content, setContent] = useState('');
  const [agentId, setAgentId] = useState('');
  const [sentiment, setSentiment] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCustomers();
  }, []);

  useEffect(() => {
    if (selectedCustomer) {
      loadProfile(selectedCustomer);
    }
  }, [selectedCustomer]);

  const loadCustomers = async () => {
    try {
      const response = await memoryAPI.searchMemories(
        'customer support interaction',
        30,
        0.5,
        false
      );
      const supportMemories = response.data.memories || [];
      
      // Extract unique customer IDs
      const uniqueCustomers = [...new Set(
        supportMemories
          .map(m => m.metadata?.customer_id)
          .filter(Boolean)
      )];
      
      setCustomers(uniqueCustomers.map(cid => ({ id: cid, name: cid })));
    } catch (error) {
      console.error('Error loading customers:', error);
    }
  };

  const loadProfile = async (customerId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/use-cases/support/customer/${customerId}/profile`
      );
      setProfile(response.data);
    } catch (error) {
      console.error('Error loading profile:', error);
      setProfile(null);
    }
  };

  const createInteraction = async () => {
    if (!content.trim() || !selectedCustomer) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/use-cases/support/interaction`,
        {
          customer_id: selectedCustomer,
          interaction_type: interactionType,
          content,
          agent_id: agentId || null,
          sentiment: sentiment || null,
          metadata: {
            created_at: new Date().toISOString()
          }
        }
      );

      setContent('');
      setSentiment('');
      loadProfile(selectedCustomer);
      loadCustomers();
      alert('Interaction recorded successfully!');
    } catch (error) {
      console.error('Error creating interaction:', error);
      alert('Failed to record interaction');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    const colors = {
      positive: '#10b981',
      negative: '#ef4444',
      neutral: '#6b7280'
    };
    return colors[sentiment] || '#6b7280';
  };

  return (
    <div className="support-dashboard">
      <div className="support-header">
        <h1>💬 Customer Support Platform</h1>
        <p>Remember customer preferences, interaction history, and build personalized experiences</p>
      </div>

      <div className="support-layout">
        {/* Customers Sidebar */}
        <div className="customers-sidebar">
          <h2>Customers</h2>
          <div className="customers-list">
            {customers.map((customer) => (
              <div
                key={customer.id}
                className={`customer-item ${selectedCustomer === customer.id ? 'active' : ''}`}
                onClick={() => setSelectedCustomer(customer.id)}
              >
                <div className="customer-icon">👤</div>
                <div className="customer-info">
                  <div className="customer-name">{customer.name}</div>
                  <div className="customer-meta">Customer</div>
                </div>
              </div>
            ))}
          </div>
          <button className="add-customer-btn">+ Add New Customer</button>
        </div>

        {/* Main Content */}
        <div className="support-main">
          {selectedCustomer ? (
            <>
              <div className="interaction-header">
                <h2>Customer Interactions</h2>
                <div className="customer-badge">
                  Customer: {selectedCustomer}
                </div>
              </div>

              {/* Create Interaction */}
              <div className="create-interaction">
                <h3>Record New Interaction</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label>Interaction Type</label>
                    <select
                      value={interactionType}
                      onChange={(e) => setInteractionType(e.target.value)}
                    >
                      <option value="chat">Chat</option>
                      <option value="email">Email</option>
                      <option value="phone">Phone</option>
                      <option value="ticket">Ticket</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Sentiment</label>
                    <select
                      value={sentiment}
                      onChange={(e) => setSentiment(e.target.value)}
                    >
                      <option value="">Select sentiment</option>
                      <option value="positive">Positive</option>
                      <option value="neutral">Neutral</option>
                      <option value="negative">Negative</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label>Agent ID</label>
                  <input
                    type="text"
                    value={agentId}
                    onChange={(e) => setAgentId(e.target.value)}
                    placeholder="e.g., agent_123"
                  />
                </div>
                <div className="form-group">
                  <label>Interaction Content</label>
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Enter interaction details, customer questions, responses..."
                    rows="6"
                  />
                </div>
                <button
                  onClick={createInteraction}
                  disabled={loading || !content.trim()}
                  className="create-btn"
                >
                  {loading ? 'Recording...' : 'Record Interaction'}
                </button>
              </div>

              {/* Customer Profile */}
              {profile && (
                <div className="customer-profile">
                  <h3>Customer Profile</h3>
                  <div className="profile-stats">
                    <div className="stat-card">
                      <div className="stat-value">{profile.total_interactions}</div>
                      <div className="stat-label">Total Interactions</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">{profile.interaction_types.length}</div>
                      <div className="stat-label">Interaction Types</div>
                    </div>
                  </div>
                  
                  <div className="interactions-list">
                    <h4>Interaction History</h4>
                    {profile.interactions.map((interaction, idx) => (
                      <div key={idx} className="interaction-card">
                        <div className="interaction-header">
                          <span className="interaction-type">{interaction.type}</span>
                          <span className="interaction-date">
                            {new Date(interaction.created_at).toLocaleDateString()}
                          </span>
                          {interaction.sentiment && (
                            <span
                              className="sentiment-badge"
                              style={{ backgroundColor: getSentimentColor(interaction.sentiment) }}
                            >
                              {interaction.sentiment}
                            </span>
                          )}
                        </div>
                        <div className="interaction-content">{interaction.content}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state-large">
              <div className="empty-icon">💬</div>
              <h2>Select a Customer</h2>
              <p>Choose a customer from the sidebar to view their interaction history</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SupportDashboard;

