import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import axios from 'axios';
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';
import './EducationDashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const EducationDashboard = () => {
  const [concepts, setConcepts] = useState([]);
  const [selectedConcept, setSelectedConcept] = useState(null);
  const [conceptName, setConceptName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [prerequisites, setPrerequisites] = useState('');
  const [loading, setLoading] = useState(false);
  const [learningPath, setLearningPath] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [activeTab, setActiveTab] = useState('create'); // 'create', 'path'

  useEffect(() => {
    loadConcepts();
  }, []);

  useEffect(() => {
    if (selectedConcept) {
      loadLearningPath(selectedConcept);
    }
  }, [selectedConcept]);

  const loadConcepts = async () => {
    try {
      const response = await memoryAPI.searchMemories(
        'educational concept learning',
        30,
        0.5,
        false
      );
      const eduMemories = response.data.memories || [];
      setConcepts(eduMemories);
    } catch (error) {
      console.error('Error loading concepts:', error);
    }
  };

  const loadLearningPath = async (conceptId) => {
    try {
      const concept = concepts.find(c => c.id === conceptId);
      if (!concept) return;

      const conceptSourceId = concept.metadata?.concept_name?.toLowerCase().replace(' ', '_') || concept.id;
      const response = await axios.get(
        `${API_BASE_URL}/use-cases/education/learning-path/${conceptSourceId}`
      );
      
      setLearningPath(response.data);
      
      // Build React Flow graph
      const flowNodes = [
        {
          id: conceptId,
          type: 'default',
          position: { x: 400, y: 200 },
          data: { label: concept.metadata?.concept_name || concept.content.substring(0, 30) },
          style: { background: '#10b981', color: 'white', width: 200 }
        }
      ];
      
      const flowEdges = [];
      
      // Add prerequisites
      response.data.prerequisites.forEach((prereq, idx) => {
        flowNodes.push({
          id: prereq.id,
          type: 'default',
          position: { x: 100, y: 100 + idx * 100 },
          data: { label: prereq.content.substring(0, 30) },
          style: { background: '#e5e7eb', width: 180 }
        });
        flowEdges.push({
          id: `prereq-${prereq.id}`,
          source: prereq.id,
          target: conceptId,
          label: 'Prerequisite',
          style: { stroke: '#10b981' }
        });
      });
      
      // Add next steps
      response.data.next_steps.forEach((next, idx) => {
        flowNodes.push({
          id: next.id,
          type: 'default',
          position: { x: 700, y: 100 + idx * 100 },
          data: { label: next.content.substring(0, 30) },
          style: { background: '#e5e7eb', width: 180 }
        });
        flowEdges.push({
          id: `next-${next.id}`,
          source: conceptId,
          target: next.id,
          label: 'Next Step',
          style: { stroke: '#3b82f6' }
        });
      });
      
      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (error) {
      console.error('Error loading learning path:', error);
    }
  };

  const createConcept = async () => {
    if (!conceptName.trim() || !description.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/use-cases/education/concept`,
        {
          concept_name: conceptName,
          description,
          category: category || 'General',
          difficulty_level: difficulty || null,
          prerequisites: prerequisites.split(',').map(p => p.trim()).filter(Boolean),
          metadata: {
            created_at: new Date().toISOString()
          }
        }
      );

      setConceptName('');
      setDescription('');
      setCategory('');
      setDifficulty('');
      setPrerequisites('');
      loadConcepts();
      alert('Concept created successfully!');
    } catch (error) {
      console.error('Error creating concept:', error);
      alert('Failed to create concept');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="education-dashboard">
      <div className="edu-header">
        <h1>🎓 Educational Platform</h1>
        <p>Connect concepts through semantic relationships and learning paths</p>
      </div>

      <div className="edu-layout">
        {/* Concepts Sidebar */}
        <div className="concepts-sidebar">
          <h2>Concepts</h2>
          <div className="concepts-list">
            {concepts.map((concept, idx) => (
              <div
                key={idx}
                className={`concept-item ${selectedConcept === concept.id ? 'active' : ''}`}
                onClick={() => setSelectedConcept(concept.id)}
              >
                <div className="concept-icon">📖</div>
                <div className="concept-info">
                  <div className="concept-name">
                    {concept.metadata?.concept_name || concept.content.substring(0, 40) + '...'}
                  </div>
                  <div className="concept-meta">
                    {concept.metadata?.difficulty_level || 'Difficulty: N/A'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="edu-main">
          <div className="edu-tabs">
            <button 
              className={`tab ${activeTab === 'create' ? 'active' : ''}`}
              onClick={() => setActiveTab('create')}
            >
              Create Concept
            </button>
            <button 
              className={`tab ${activeTab === 'path' ? 'active' : ''}`}
              onClick={() => setActiveTab('path')}
            >
              Learning Path
            </button>
          </div>

          <div className="edu-content">
            {/* Create Concept */}
            {activeTab === 'create' && (
            <div className="create-concept">
              <h2>Create New Concept</h2>
              <div className="form-group">
                <label>Concept Name</label>
                <input
                  type="text"
                  value={conceptName}
                  onChange={(e) => setConceptName(e.target.value)}
                  placeholder="e.g., Machine Learning, Algebra, Photosynthesis"
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe the concept in detail..."
                  rows="6"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Category</label>
                  <input
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    placeholder="e.g., Mathematics, Science, History"
                  />
                </div>
                <div className="form-group">
                  <label>Difficulty Level</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                  >
                    <option value="">Select difficulty</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Prerequisites (comma-separated)</label>
                <input
                  type="text"
                  value={prerequisites}
                  onChange={(e) => setPrerequisites(e.target.value)}
                  placeholder="e.g., Basic Math, Introduction to Programming"
                />
              </div>
              <button
                onClick={createConcept}
                disabled={loading || !conceptName.trim() || !description.trim()}
                className="create-btn"
              >
                {loading ? 'Creating...' : 'Create Concept'}
              </button>
            </div>
            )}

            {/* Learning Path */}
            {activeTab === 'path' && (
              <div className="learning-path-section">
                {selectedConcept && learningPath ? (
              <div className="learning-path">
                <h2>Learning Path</h2>
                <div className="path-info">
                  <div className="path-section">
                    <h3>Prerequisites ({learningPath.prerequisites.length})</h3>
                    {learningPath.prerequisites.length > 0 ? (
                      <ul>
                        {learningPath.prerequisites.map((prereq, idx) => (
                          <li key={idx}>{prereq.content}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty">No prerequisites</p>
                    )}
                  </div>
                  <div className="path-section">
                    <h3>Next Steps ({learningPath.next_steps.length})</h3>
                    {learningPath.next_steps.length > 0 ? (
                      <ul>
                        {learningPath.next_steps.map((next, idx) => (
                          <li key={idx}>{next.content}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty">No next steps defined</p>
                    )}
                  </div>
                </div>
                {nodes.length > 0 && (
                  <div className="graph-view" style={{ height: '500px', marginTop: '2rem' }}>
                    <ReactFlow nodes={nodes} edges={edges} fitView>
                      <Background />
                      <Controls />
                      <MiniMap />
                    </ReactFlow>
                  </div>
                )}
              </div>
              ) : (
                <div className="no-selection">
                  <p>Please select a concept from the sidebar to view its learning path.</p>
                </div>
              )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EducationDashboard;

