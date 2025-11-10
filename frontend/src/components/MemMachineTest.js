import React, { useState } from 'react';
import { memoryAPI } from '../services/api';
import './MemMachineTest.css';

const MemMachineTest = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [searchResults, setSearchResults] = useState(null);
  const [testSession, setTestSession] = useState({
    group_id: 'test_group',
    agent_id: ['test_agent'],
    user_id: ['test_user'],
    session_id: `session_${Date.now()}`,
  });
  const [searchQuery, setSearchQuery] = useState('');

  const testHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await memoryAPI.memmachine.healthCheck();
      setStatus(response.data);
    } catch (err) {
      setError(err.response?.data || err.message);
    } finally {
      setLoading(false);
    }
  };

  const testGetSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await memoryAPI.memmachine.getSessions();
      setSessions(response.data || []);
    } catch (err) {
      setError(err.response?.data || err.message);
    } finally {
      setLoading(false);
    }
  };

  const testCreateMemory = async () => {
    setLoading(true);
    setError(null);
    try {
      const episode = {
        producer: 'test_user',
        produced_for: 'test_agent',
        episode_content: 'This is a test memory from the frontend dashboard',
        episode_type: 'test',
      };
      const response = await memoryAPI.memmachine.createMemory(testSession, episode);
      setStatus({ success: true, message: 'Memory created!', data: response.data });
    } catch (err) {
      setError(err.response?.data || err.message);
    } finally {
      setLoading(false);
    }
  };

  const testSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await memoryAPI.memmachine.searchMemories(testSession, searchQuery, 5);
      setSearchResults(response.data);
    } catch (err) {
      setError(err.response?.data || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="memmachine-test">
      <h2>MemMachine Integration Test</h2>
      
      <div className="test-section">
        <h3>Connection Test</h3>
        <button onClick={testHealth} disabled={loading}>
          Test MemMachine Health
        </button>
        {status && (
          <div className="status-box">
            <pre>{JSON.stringify(status, null, 2)}</pre>
          </div>
        )}
      </div>

      <div className="test-section">
        <h3>Session Management</h3>
        <div className="session-config">
          <label>Group ID:</label>
          <input
            type="text"
            value={testSession.group_id}
            onChange={(e) => setTestSession({...testSession, group_id: e.target.value})}
          />
          <label>Agent ID:</label>
          <input
            type="text"
            value={testSession.agent_id[0]}
            onChange={(e) => setTestSession({...testSession, agent_id: [e.target.value]})}
          />
          <label>User ID:</label>
          <input
            type="text"
            value={testSession.user_id[0]}
            onChange={(e) => setTestSession({...testSession, user_id: [e.target.value]})}
          />
          <label>Session ID:</label>
          <input
            type="text"
            value={testSession.session_id}
            onChange={(e) => setTestSession({...testSession, session_id: e.target.value})}
          />
        </div>
        <button onClick={testGetSessions} disabled={loading}>
          Get All Sessions
        </button>
        {sessions.length > 0 && (
          <div className="status-box">
            <p>Found {sessions.length} sessions:</p>
            <pre>{JSON.stringify(sessions, null, 2)}</pre>
          </div>
        )}
      </div>

      <div className="test-section">
        <h3>Create Memory</h3>
        <button onClick={testCreateMemory} disabled={loading}>
          Create Test Memory
        </button>
      </div>

      <div className="test-section">
        <h3>Search Memories</h3>
        <div className="search-box">
          <input
            type="text"
            placeholder="Enter search query..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && testSearch()}
          />
          <button onClick={testSearch} disabled={loading || !searchQuery.trim()}>
            Search
          </button>
        </div>
        {searchResults && (
          <div className="status-box">
            <p>Search Results:</p>
            <pre>{JSON.stringify(searchResults, null, 2)}</pre>
          </div>
        )}
      </div>

      {error && (
        <div className="error-box">
          <strong>Error:</strong>
          <pre>{JSON.stringify(error, null, 2)}</pre>
        </div>
      )}

      {loading && <div className="loading">Loading...</div>}
    </div>
  );
};

export default MemMachineTest;

