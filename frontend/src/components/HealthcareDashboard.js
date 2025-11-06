import React, { useState, useEffect } from 'react';
import { memoryAPI } from '../services/api';
import axios from 'axios';
import './HealthcareDashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const HealthcareDashboard = () => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [recordType, setRecordType] = useState('examination');
  const [content, setContent] = useState('');
  const [doctorId, setDoctorId] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPatients();
  }, []);

  useEffect(() => {
    if (selectedPatient) {
      loadTimeline(selectedPatient);
    }
  }, [selectedPatient]);

  const loadPatients = async () => {
    try {
      const response = await memoryAPI.searchMemories(
        'healthcare patient record',
        30,
        0.5,
        false
      );
      const patientMemories = response.data.memories || [];
      
      // Extract unique patient IDs
      const uniquePatients = [...new Set(
        patientMemories
          .map(m => m.metadata?.patient_id)
          .filter(Boolean)
      )];
      
      setPatients(uniquePatients.map(pid => ({ id: pid, name: pid })));
    } catch (error) {
      console.error('Error loading patients:', error);
    }
  };

  const loadTimeline = async (patientId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/use-cases/healthcare/patient/${patientId}/timeline`
      );
      setTimeline(response.data);
    } catch (error) {
      console.error('Error loading timeline:', error);
      setTimeline(null);
    }
  };

  const createRecord = async () => {
    if (!content.trim() || !selectedPatient) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/use-cases/healthcare/record`,
        {
          patient_id: selectedPatient,
          record_type: recordType,
          content,
          doctor_id: doctorId || null,
          metadata: {
            created_at: new Date().toISOString()
          }
        }
      );

      setContent('');
      loadTimeline(selectedPatient);
      loadPatients();
      alert('Record created successfully!');
    } catch (error) {
      console.error('Error creating record:', error);
      alert('Failed to create record');
    } finally {
      setLoading(false);
    }
  };

  const getRecordTypeColor = (type) => {
    const colors = {
      examination: '#3b82f6',
      diagnosis: '#ef4444',
      treatment: '#10b981',
      medication: '#f59e0b'
    };
    return colors[type] || '#6b7280';
  };

  return (
    <div className="healthcare-dashboard">
      <div className="healthcare-header">
        <h1>🏥 Healthcare System</h1>
        <p>Track patient information evolution and medical relationships with full audit trails</p>
      </div>

      <div className="healthcare-layout">
        {/* Patients Sidebar */}
        <div className="patients-sidebar">
          <h2>Patients</h2>
          <div className="patients-list">
            {patients.map((patient) => (
              <div
                key={patient.id}
                className={`patient-item ${selectedPatient === patient.id ? 'active' : ''}`}
                onClick={() => setSelectedPatient(patient.id)}
              >
                <div className="patient-icon">👤</div>
                <div className="patient-info">
                  <div className="patient-name">{patient.name}</div>
                  <div className="patient-meta">Patient ID</div>
                </div>
              </div>
            ))}
          </div>
          <button className="add-patient-btn">+ Add New Patient</button>
        </div>

        {/* Main Content */}
        <div className="healthcare-main">
          {selectedPatient ? (
            <>
              <div className="record-header">
                <h2>Patient Records</h2>
                <div className="patient-info-badge">
                  Patient: {selectedPatient}
                </div>
              </div>

              {/* Create Record */}
              <div className="create-record">
                <h3>Create New Record</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label>Record Type</label>
                    <select
                      value={recordType}
                      onChange={(e) => setRecordType(e.target.value)}
                    >
                      <option value="examination">Examination</option>
                      <option value="diagnosis">Diagnosis</option>
                      <option value="treatment">Treatment</option>
                      <option value="medication">Medication</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Doctor ID</label>
                    <input
                      type="text"
                      value={doctorId}
                      onChange={(e) => setDoctorId(e.target.value)}
                      placeholder="e.g., doctor_123"
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>Record Content</label>
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Enter record details, findings, notes..."
                    rows="6"
                  />
                </div>
                <button
                  onClick={createRecord}
                  disabled={loading || !content.trim()}
                  className="create-btn"
                  style={{ backgroundColor: getRecordTypeColor(recordType) }}
                >
                  {loading ? 'Creating...' : `Create ${recordType.charAt(0).toUpperCase() + recordType.slice(1)} Record`}
                </button>
              </div>

              {/* Timeline */}
              {timeline && (
                <div className="timeline-section">
                  <h3>Medical Timeline</h3>
                  <div className="timeline-stats">
                    <div className="stat-item">
                      <span className="stat-label">Total Records:</span>
                      <span className="stat-value">{timeline.total_records}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Record Types:</span>
                      <span className="stat-value">{timeline.record_types.join(', ')}</span>
                    </div>
                  </div>
                  <div className="timeline">
                    {timeline.records.map((record, idx) => (
                      <div key={idx} className="timeline-item">
                        <div className="timeline-date">
                          {new Date(record.created_at).toLocaleDateString()}
                        </div>
                        <div className="timeline-content">
                          <div className="timeline-header">
                            <span className="timeline-type" style={{ backgroundColor: getRecordTypeColor(record.record_type) }}>
                              {record.record_type}
                            </span>
                            {record.doctor_id && (
                              <span className="timeline-doctor">Dr. {record.doctor_id}</span>
                            )}
                          </div>
                          <div className="timeline-body">{record.content}</div>
                          {record.audit_trail && (
                            <div className="timeline-audit">
                              <strong>Audit Trail:</strong> Created by {record.audit_trail.created_by} at {new Date(record.audit_trail.created_at).toLocaleString()}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state-large">
              <div className="empty-icon">🏥</div>
              <h2>Select a Patient</h2>
              <p>Choose a patient from the sidebar to view their medical timeline</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HealthcareDashboard;

