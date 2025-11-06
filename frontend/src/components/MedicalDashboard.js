import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import './MedicalDashboard.css';

const MedicalDashboard = () => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [examinations, setExaminations] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadPatients();
    loadStats();
  }, []);

  useEffect(() => {
    if (selectedPatient) {
      loadExaminations(selectedPatient);
    }
  }, [selectedPatient]);

  const loadPatients = async () => {
    try {
      const response = await memoryAPI.searchMemories(
        'medical patient examination',
        20,
        0.5,
        false
      );
      // Filter for patient-related memories
      const patientMemories = response.data.memories || [];
      setPatients(patientMemories);
    } catch (error) {
      console.error('Error loading patients:', error);
    }
  };

  const loadExaminations = async (patientId) => {
    try {
      const response = await memoryAPI.searchMemories(
        `patient ${patientId} examination`,
        20,
        0.5,
        true
      );
      setExaminations(response.data.memories || []);
    } catch (error) {
      console.error('Error loading examinations:', error);
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

  const createExamination = async () => {
    if (!newNote.trim() || !selectedPatient) return;

    setLoading(true);
    try {
      const memoryData = {
        content: newNote,
        source_type: 'examination',
        source_id: `exam_${Date.now()}`,
        metadata: {
          patient_id: selectedPatient,
          date: new Date().toISOString(),
          type: 'examination',
          doctor: 'Dr. Smith'
        }
      };

      await memoryAPI.createMemory(memoryData);
      setNewNote('');
      loadExaminations(selectedPatient);
      loadStats();
    } catch (error) {
      console.error('Error creating examination:', error);
      alert('Failed to create examination note');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="medical-dashboard">
      <div className="medical-header">
        <h1>🏥 Medical Examination Platform</h1>
        <p>Manage patient records, examination notes, and medical history</p>
      </div>

      <div className="medical-layout">
        {/* Patient Sidebar */}
        <div className="patient-sidebar">
          <h2>Patients</h2>
          <div className="patient-list">
            {patients.map((patient, idx) => (
              <div
                key={idx}
                className={`patient-item ${selectedPatient === patient.id ? 'active' : ''}`}
                onClick={() => setSelectedPatient(patient.id)}
              >
                <div className="patient-icon">👤</div>
                <div className="patient-info">
                  <div className="patient-name">
                    {patient.metadata?.patient_name || `Patient ${patient.id.slice(-6)}`}
                  </div>
                  <div className="patient-meta">
                    {patient.metadata?.age ? `Age: ${patient.metadata.age}` : 'No age info'}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button className="add-patient-btn">+ Add New Patient</button>
        </div>

        {/* Main Content */}
        <div className="medical-main">
          {selectedPatient ? (
            <>
              <div className="examination-header">
                <h2>Examination Notes</h2>
                <div className="examination-stats">
                  <div className="stat-item">
                    <span className="stat-label">Total Examinations:</span>
                    <span className="stat-value">{examinations.length}</span>
                  </div>
                </div>
              </div>

              <div className="new-examination">
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Enter examination notes, symptoms, diagnosis, treatment plan..."
                  rows="4"
                />
                <button
                  onClick={createExamination}
                  disabled={loading || !newNote.trim()}
                  className="create-btn"
                >
                  {loading ? 'Creating...' : 'Create Examination Note'}
                </button>
              </div>

              <div className="examinations-list">
                <h3>Examination History</h3>
                {examinations.length === 0 ? (
                  <div className="empty-state">
                    <p>No examination notes found. Create your first note above.</p>
                  </div>
                ) : (
                  examinations.map((exam, idx) => (
                    <div key={idx} className="examination-card">
                      <div className="examination-header">
                        <div className="examination-date">
                          {new Date(exam.metadata?.date || exam.created_at).toLocaleDateString()}
                        </div>
                        <div className="examination-doctor">
                          {exam.metadata?.doctor || 'Dr. Unknown'}
                        </div>
                      </div>
                      <div className="examination-content">{exam.content}</div>
                      {exam.metadata?.symptoms && (
                        <div className="examination-tags">
                          {exam.metadata.symptoms.map((symptom, i) => (
                            <span key={i} className="tag symptom-tag">
                              {symptom}
                            </span>
                          ))}
                        </div>
                      )}
                      {exam.metadata?.diagnosis && (
                        <div className="diagnosis">
                          <strong>Diagnosis:</strong> {exam.metadata.diagnosis}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <div className="empty-state-large">
              <div className="empty-icon">🏥</div>
              <h2>Select a Patient</h2>
              <p>Choose a patient from the sidebar to view their examination history</p>
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
                <div className="stat-value">
                  {stats.relationships?.total || 0}
                </div>
                <div className="stat-label">Relationships</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MedicalDashboard;

