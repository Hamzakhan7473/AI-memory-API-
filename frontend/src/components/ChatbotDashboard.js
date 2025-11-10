import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import axios from 'axios';
import './ChatbotDashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const ChatbotDashboard = () => {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [userId] = useState(`user_${Date.now()}`);
  const [sessionId, setSessionId] = useState(`session_${Date.now()}`);

  useEffect(() => {
    loadSessions();
    if (selectedSession) {
      loadHistory(selectedSession);
    }
  }, [selectedSession]);

  const loadSessions = async () => {
    try {
      // Use dedicated sessions endpoint
      const response = await axios.get(
        `${API_BASE_URL}/use-cases/chatbots/sessions`,
        {
          params: {
            limit: 50
          }
        }
      );
      
      const sessionList = response.data.sessions || [];
      setSessions(sessionList.map(s => ({
        id: s.session_id,
        name: s.session_id,
        message_count: s.message_count,
        last_message: s.last_message
      })));
      
      // If no selected session and we have sessions, select the first one
      if (!selectedSession && sessionList.length > 0) {
        setSelectedSession(sessionList[0].session_id);
        setSessionId(sessionList[0].session_id);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
      // Fallback to empty sessions
      setSessions([]);
    }
  };

  const loadHistory = async (sessionId) => {
    if (!sessionId) return;
    
    try {
      const response = await axios.get(
        `${API_BASE_URL}/use-cases/chatbots/session/${sessionId}/history`
      );
      const history = response.data.history || [];
      
      // Format messages for display
      const formattedMessages = history.map(msg => ({
        role: msg.role || 'user',
        content: msg.content || msg.message || '',
        timestamp: msg.timestamp || new Date().toISOString(),
        citations: msg.citations || [],
        memory_id: msg.memory_id
      }));
      
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error loading history:', error);
      setMessages([]);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/use-cases/chatbots/message`,
        {
          user_id: userId,
          session_id: sessionId,
          message: newMessage,
          context: {
            timestamp: new Date().toISOString()
          }
        }
      );

      // Add user message and bot response
      setMessages(prev => [
        ...prev,
        {
          role: 'user',
          content: newMessage,
          timestamp: new Date().toISOString()
        },
        {
          role: 'assistant',
          content: response.data.response,
          citations: response.data.citations,
          timestamp: new Date().toISOString()
        }
      ]);

      setNewMessage('');
      loadSessions();
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = () => {
    const newSessionId = `session_${Date.now()}`;
    setSessionId(newSessionId);
    setSelectedSession(newSessionId);
    setMessages([]);
    // Reload sessions to show the new one
    setTimeout(() => loadSessions(), 500);
  };

  return (
    <div className="chatbot-dashboard">
      <div className="chatbot-header">
        <h1>🤖 AI Chatbot Platform</h1>
        <p>Enable chatbots to remember context and build relationships between conversations</p>
      </div>

      <div className="chatbot-layout">
        {/* Sessions Sidebar */}
        <div className="sessions-sidebar">
          <div className="sidebar-header">
            <h2>Conversations</h2>
            <button onClick={createNewSession} className="new-session-btn">
              + New Session
            </button>
          </div>
          <div className="sessions-list">
            {sessions.length === 0 ? (
              <div className="no-sessions">
                <p>No conversations yet. Start a new session!</p>
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.id}
                  className={`session-item ${selectedSession === session.id ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedSession(session.id);
                    setSessionId(session.id);
                  }}
                >
                  <div className="session-icon">💬</div>
                  <div className="session-info">
                    <div className="session-name">
                      {session.name || session.id}
                    </div>
                    <div className="session-meta">
                      {session.message_count ? `${session.message_count} messages` : 'New session'}
                      {session.last_message && (
                        <span className="session-time">
                          {new Date(session.last_message).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Interface */}
        <div className="chat-main">
          <div className="chat-container">
            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="empty-chat">
                  <div className="empty-icon">🤖</div>
                  <h2>Start a Conversation</h2>
                  <p>Send a message to begin chatting with the AI assistant</p>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role}`}>
                    <div className="message-header">
                      <span className="message-role">{msg.role === 'user' ? 'You' : 'AI Assistant'}</span>
                      <span className="message-time">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="message-content">{msg.content}</div>
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="message-citations">
                        <strong>Sources:</strong>
                        {msg.citations.map((cite, i) => (
                          <span key={i} className="citation-tag">
                            [{i + 1}]
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="chat-input">
              <textarea
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
                rows="3"
                disabled={loading}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !newMessage.trim()}
                className="send-btn"
              >
                {loading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotDashboard;

