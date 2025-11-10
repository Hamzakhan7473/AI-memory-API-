import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import LandingPage from './LandingPage';
import Dashboard from './components/Dashboard';
import MemorySearch from './components/MemorySearch';
import MemoryForm from './components/MemoryForm';
import GraphStats from './components/GraphStats';
import MemMachineTest from './components/MemMachineTest';
import AdvancedGraphSearch from './components/AdvancedGraphSearch';
import UseCaseSelector from './components/UseCaseSelector';

function DashboardApp() {
  const [activeTab, setActiveTab] = useState('graph');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Memory Platform</h1>
        <nav className="nav-tabs">
          <button 
            className={activeTab === 'graph' ? 'active' : ''}
            onClick={() => setActiveTab('graph')}
          >
            Knowledge Graph
          </button>
          <button 
            className={activeTab === 'search' ? 'active' : ''}
            onClick={() => setActiveTab('search')}
          >
            Search
          </button>
          <button 
            className={activeTab === 'add' ? 'active' : ''}
            onClick={() => setActiveTab('add')}
          >
            Add Memory
          </button>
          <button 
            className={activeTab === 'stats' ? 'active' : ''}
            onClick={() => setActiveTab('stats')}
          >
            Statistics
          </button>
          <button 
            className={activeTab === 'memmachine' ? 'active' : ''}
            onClick={() => setActiveTab('memmachine')}
          >
            MemMachine Test
          </button>
          <button 
            className={activeTab === 'advanced-search' ? 'active' : ''}
            onClick={() => setActiveTab('advanced-search')}
          >
            Advanced Search
          </button>
          <button 
            className={activeTab === 'use-cases' ? 'active' : ''}
            onClick={() => setActiveTab('use-cases')}
          >
            Use Cases
          </button>
        </nav>
      </header>

      <main className="App-main">
        {activeTab === 'graph' && (
          <Dashboard refreshTrigger={refreshTrigger} onRefresh={handleRefresh} />
        )}
        {activeTab === 'search' && (
          <MemorySearch />
        )}
        {activeTab === 'add' && (
          <MemoryForm onSuccess={handleRefresh} />
        )}
        {activeTab === 'stats' && (
          <GraphStats refreshTrigger={refreshTrigger} />
        )}
        {activeTab === 'memmachine' && (
          <MemMachineTest />
        )}
        {activeTab === 'advanced-search' && (
          <AdvancedGraphSearch />
        )}
        {activeTab === 'use-cases' && (
          <UseCaseSelector />
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<DashboardApp />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;

