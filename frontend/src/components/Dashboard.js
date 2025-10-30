import React, { useState, useEffect, useRef } from 'react';
import { Network } from 'vis-network/standalone';
import { memoryAPI } from '../services/api';
import MemoryDetails from './MemoryDetails';
import './Dashboard.css';

const Dashboard = ({ refreshTrigger, onRefresh }) => {
  const [graphData, setGraphData] = useState(null);
  const [network, setNetwork] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedMemory, setSelectedMemory] = useState(null);
  const [filters, setFilters] = useState({
    relationshipTypes: '',
    onlyLatest: true,
    limit: 100,
  });
  
  const networkRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    loadGraphData();
  }, [refreshTrigger, filters]);

  useEffect(() => {
    if (graphData && containerRef.current) {
      initializeNetwork();
    }
  }, [graphData]);

  const loadGraphData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await memoryAPI.getGraphVisualization(
        filters.limit,
        filters.relationshipTypes || null,
        filters.onlyLatest
      );
      
      setGraphData(response.data);
    } catch (err) {
      setError(err.message || 'Failed to load graph data');
      console.error('Error loading graph:', err);
    } finally {
      setLoading(false);
    }
  };

  const initializeNetwork = () => {
    if (!graphData || !containerRef.current) return;

    // Prepare nodes for vis-network
    const nodes = graphData.nodes.map(node => ({
      id: node.id,
      label: node.label,
      title: node.content.substring(0, 200),
      color: node.is_latest ? '#61dafb' : '#999',
      shape: 'box',
      font: { size: 12 },
    }));

    // Prepare edges
    const edges = graphData.edges.map(edge => ({
      id: edge.id,
      from: edge.source,
      to: edge.target,
      label: edge.type,
      color: getEdgeColor(edge.type),
      width: 2 + edge.confidence * 3,
      arrows: 'to',
      title: `Type: ${edge.type}\nConfidence: ${(edge.confidence * 100).toFixed(1)}%`,
    }));

    const data = { nodes, edges };

    const options = {
      nodes: {
        borderWidth: 2,
        shadow: true,
        font: {
          color: '#333',
        },
      },
      edges: {
        smooth: {
          type: 'curvedCW',
          roundness: 0.3,
        },
        font: {
          size: 10,
          align: 'middle',
        },
      },
      physics: {
        enabled: true,
        stabilization: {
          iterations: 200,
        },
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.3,
          springLength: 95,
          springConstant: 0.04,
          damping: 0.09,
        },
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true,
      },
    };

    if (networkRef.current) {
      networkRef.current.destroy();
    }

    const net = new Network(containerRef.current, data, options);
    
    // Handle node selection
    net.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        setSelectedNode(nodeId);
        loadMemoryDetails(nodeId);
      } else {
        setSelectedNode(null);
        setSelectedMemory(null);
      }
    });

    // Handle double-click to fit
    net.on('doubleClick', (params) => {
      if (params.nodes.length > 0) {
        net.focus(params.nodes[0], {
          scale: 1.5,
          animation: true,
        });
      }
    });

    networkRef.current = net;
    setNetwork(net);
  };

  const getEdgeColor = (type) => {
    const colors = {
      update: '#dc3545',  // Red for updates
      extend: '#28a745',  // Green for extends
      derive: '#ffc107',  // Yellow for derives
    };
    return colors[type] || '#666';
  };

  const loadMemoryDetails = async (memoryId) => {
    try {
      const response = await memoryAPI.getMemoryDetails(memoryId);
      setSelectedMemory(response.data);
    } catch (err) {
      console.error('Error loading memory details:', err);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return <div className="loading">Loading graph...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-controls">
        <div className="card">
          <h3>Graph Filters</h3>
          <div className="form-group">
            <label>Relationship Types (comma-separated):</label>
            <input
              type="text"
              value={filters.relationshipTypes}
              onChange={(e) => handleFilterChange('relationshipTypes', e.target.value)}
              placeholder="update,extend,derive"
            />
          </div>
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={filters.onlyLatest}
                onChange={(e) => handleFilterChange('onlyLatest', e.target.checked)}
              />
              {' '}Only Latest Memories
            </label>
          </div>
          <div className="form-group">
            <label>Limit:</label>
            <input
              type="number"
              value={filters.limit}
              onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
              min="10"
              max="500"
            />
          </div>
          <button onClick={loadGraphData}>Refresh Graph</button>
        </div>

        {graphData && graphData.stats && (
          <div className="card">
            <h3>Graph Statistics</h3>
            <ul className="stats-list">
              <li>Total Memories: {graphData.stats.total_memories}</li>
              <li>Latest Memories: {graphData.stats.latest_memories}</li>
              <li>Total Relationships: {graphData.stats.total_relationships}</li>
            </ul>
          </div>
        )}
      </div>

      <div className="dashboard-main">
        <div className="graph-container">
          <div className="graph-header">
            <h2>Knowledge Graph</h2>
            <div className="legend">
              <span className="legend-item">
                <span className="legend-color" style={{ backgroundColor: '#61dafb' }}></span>
                Latest Memory
              </span>
              <span className="legend-item">
                <span className="legend-color" style={{ backgroundColor: '#999' }}></span>
                Outdated Memory
              </span>
              <span className="legend-item">
                <span className="legend-edge" style={{ borderColor: '#dc3545' }}></span>
                Update
              </span>
              <span className="legend-item">
                <span className="legend-edge" style={{ borderColor: '#28a745' }}></span>
                Extend
              </span>
              <span className="legend-item">
                <span className="legend-edge" style={{ borderColor: '#ffc107' }}></span>
                Derive
              </span>
            </div>
          </div>
          <div ref={containerRef} className="network-container"></div>
        </div>

        {selectedMemory && (
          <MemoryDetails
            memory={selectedMemory}
            onClose={() => {
              setSelectedNode(null);
              setSelectedMemory(null);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard;

