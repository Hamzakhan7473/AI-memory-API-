import React, { useState } from 'react';
import './UseCaseSelector.css';
import MedicalDashboard from './MedicalDashboard';
import FinanceDashboard from './FinanceDashboard';
import ElectionDashboard from './ElectionDashboard';
import ChatbotDashboard from './ChatbotDashboard';
import KnowledgeBaseDashboard from './KnowledgeBaseDashboard';
import EducationDashboard from './EducationDashboard';
import HealthcareDashboard from './HealthcareDashboard';
import SupportDashboard from './SupportDashboard';
import ResearchDashboard from './ResearchDashboard';

const UseCaseSelector = () => {
  const [selectedUseCase, setSelectedUseCase] = useState(null);

  const useCases = [
    {
      id: 'chatbots',
      title: 'AI Chatbots',
      icon: '🤖',
      description: 'Remember context and build relationships between conversations over time',
      color: '#ef4444'
    },
    {
      id: 'knowledge-base',
      title: 'Knowledge Bases',
      icon: '📚',
      description: 'Transform documents into searchable knowledge graphs with semantic understanding',
      color: '#f59e0b'
    },
    {
      id: 'education',
      title: 'Educational Platforms',
      icon: '🎓',
      description: 'Connect concepts through semantic relationships and learning paths',
      color: '#10b981'
    },
    {
      id: 'healthcare',
      title: 'Healthcare Systems',
      icon: '🏥',
      description: 'Track patient information evolution and medical relationships with full audit trails',
      color: '#3b82f6'
    },
    {
      id: 'support',
      title: 'Customer Support',
      icon: '💬',
      description: 'Remember customer preferences, interaction history, and build personalized experiences',
      color: '#8b5cf6'
    },
    {
      id: 'research',
      title: 'Research Tools',
      icon: '🔬',
      description: 'Build knowledge graphs from research papers, documents, and scholarly articles',
      color: '#ec4899'
    },
    {
      id: 'medical',
      title: 'Medical Examination',
      icon: '🏥',
      description: 'Patient records, doctor notes, and medical history management',
      color: '#10b981'
    },
    {
      id: 'finance',
      title: 'Financial Advisory',
      icon: '💰',
      description: 'Client portfolios, market insights, and investment strategies',
      color: '#3b82f6'
    },
    {
      id: 'election',
      title: 'NYC Mayoral Election',
      icon: '🗳️',
      description: 'Candidate tracking, policy positions, and campaign promises',
      color: '#8b5cf6'
    }
  ];

  const renderDashboard = () => {
    switch (selectedUseCase) {
      case 'chatbots':
        return <ChatbotDashboard />;
      case 'knowledge-base':
        return <KnowledgeBaseDashboard />;
      case 'education':
        return <EducationDashboard />;
      case 'healthcare':
        return <HealthcareDashboard />;
      case 'support':
        return <SupportDashboard />;
      case 'research':
        return <ResearchDashboard />;
      case 'medical':
        return <MedicalDashboard />;
      case 'finance':
        return <FinanceDashboard />;
      case 'election':
        return <ElectionDashboard />;
      default:
        return null;
    }
  };

  return (
    <div className="use-case-container">
      {!selectedUseCase ? (
        <div className="use-case-selector">
          <div className="use-case-header">
            <h1>AI Memory Platform - Use Cases</h1>
            <p>Select a use case to explore domain-specific features</p>
          </div>
          
          <div className="use-case-grid">
            {useCases.map((useCase) => (
              <div
                key={useCase.id}
                className="use-case-card"
                onClick={() => setSelectedUseCase(useCase.id)}
                style={{ borderTopColor: useCase.color }}
              >
                <div className="use-case-icon">{useCase.icon}</div>
                <h2>{useCase.title}</h2>
                <p>{useCase.description}</p>
                <button className="use-case-button" style={{ backgroundColor: useCase.color }}>
                  Open Dashboard →
                </button>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="use-case-dashboard">
          <button 
            className="back-button"
            onClick={() => setSelectedUseCase(null)}
          >
            ← Back to Use Cases
          </button>
          {renderDashboard()}
        </div>
      )}
    </div>
  );
};

export default UseCaseSelector;

