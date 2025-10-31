import React from 'react';
import './LandingPage.css';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="logo">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7V10C2 15.55 5.42 20.74 12 22C18.58 20.74 22 15.55 22 10V7L12 2Z" fill="url(#gradient)" stroke="currentColor" strokeWidth="1.5"/>
              <defs>
                <linearGradient id="gradient" x1="2" y1="7" x2="22" y2="17" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#00d4ff"/>
                  <stop offset="0.5" stopColor="#5b8def"/>
                  <stop offset="1" stopColor="#b721ff"/>
                </linearGradient>
              </defs>
            </svg>
            <span>AI Memory API</span>
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#use-cases">Use Cases</a>
            <a href="#docs">Docs</a>
            <Link to="/dashboard" className="nav-button">Dashboard</Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-badge">Open Source • Free Forever</div>
          <h1 className="hero-title">
            Build AI agents with a powerful <span className="gradient-text">Memory API</span>
          </h1>
          <p className="hero-subtitle">
            Transform text and PDFs into dynamic knowledge graphs with semantic understanding. 
            Track how memories evolve and connect over time.
          </p>
          <div className="hero-buttons">
            <Link to="/dashboard" className="btn-primary">Get Started Free</Link>
            <a href="https://github.com/Hamzakhan7473/AI-memory-API-" target="_blank" rel="noopener noreferrer" className="btn-secondary">View on GitHub</a>
          </div>
          <div className="hero-stats">
            <div className="hero-stat">
              <strong>239+</strong> embedding dimensions
            </div>
            <div className="hero-stat">
              <strong>&lt;400ms</strong> average latency
            </div>
            <div className="hero-stat">
              <strong>3</strong> relationship types
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Powerful & Efficient AI Memory</h2>
            <p className="section-subtitle">Everything you need to build intelligent memory layers for AI applications</p>
          </div>
          <div className="features-grid">
            <FeatureCard
              icon={<SemanticIcon />}
              title="Semantic Understanding"
              description="Transform text and PDFs into intelligent knowledge graphs using vector embeddings for true semantic search"
            />
            <FeatureCard
              icon={<RelationshipIcon />}
              title="Dynamic Relationships"
              description="Three relationship types (Update, Extend, Derive) create intelligent connections between memories"
            />
            <FeatureCard
              icon={<SpeedIcon />}
              title="Low Latency"
              description="Optimized architecture delivers sub-400ms response times with efficient graph traversal"
            />
            <FeatureCard
              icon={<VisualizationIcon />}
              title="Real-time Visualization"
              description="Interactive graph dashboard shows how memories evolve and connect in real-time"
            />
            <FeatureCard
              icon={<SearchIcon />}
              title="Semantic Search"
              description="Find relevant memories through meaning, not keywords. Powered by advanced vector similarity"
            />
            <FeatureCard
              icon={<VersionIcon />}
              title="Version Lineage"
              description="Track complete evolution history of memories with full version lineage and audit trails"
            />
          </div>
        </div>
      </section>

      {/* Knowledge Graph Demo */}
      <section className="demo-section">
        <div className="container">
          <div className="demo-content">
            <div className="demo-text">
              <h2 className="section-title">Build dynamic knowledge graphs from any content</h2>
              <p className="section-subtitle">
                Upload PDFs or enter text, and watch as our system automatically creates semantic connections, 
                tracks versions, and builds a living knowledge graph that evolves over time.
              </p>
              <ul className="demo-features">
                <li>Automatic text chunking and processing</li>
                <li>Intelligent relationship detection</li>
                <li>Version tracking and lineage</li>
                <li>Real-time graph visualization</li>
              </ul>
            </div>
            <div className="demo-visual">
              <div className="graph-preview">
                <div className="graph-node node-1">
                  <div className="node-content">Memory 1</div>
                  <div className="node-label">Text Input</div>
                </div>
                <div className="graph-connection">
                  <svg viewBox="0 0 100 20" className="connection-line">
                    <path d="M 0 10 Q 50 5 100 10" stroke="#667eea" strokeWidth="2" fill="none" strokeDasharray="5,5"/>
                  </svg>
                  <span className="connection-label">Extend</span>
                </div>
                <div className="graph-node node-2">
                  <div className="node-content">Memory 2</div>
                  <div className="node-label">PDF Chunk</div>
                </div>
                <div className="graph-connection">
                  <svg viewBox="0 0 100 20" className="connection-line">
                    <path d="M 0 10 Q 50 15 100 10" stroke="#764ba2" strokeWidth="2" fill="none"/>
                  </svg>
                  <span className="connection-label">Derive</span>
                </div>
                <div className="graph-node node-3">
                  <div className="node-content">Memory 3</div>
                  <div className="node-label">Inferred</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start */}
      <section id="demo" className="quick-start">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Get started in minutes</h2>
            <p className="section-subtitle">Simple API, powerful results</p>
          </div>
          <div className="code-example">
            <div className="code-tabs">
              <button className="code-tab active">Python</button>
              <button className="code-tab">cURL</button>
            </div>
            <pre className="code-block">
{`import requests

# Create a memory
response = requests.post(
    "http://localhost:8000/api/memories/",
    json={
        "content": "User works at Supermemory",
        "metadata": {"source": "conversation"}
    }
)

# Semantic search
results = requests.post(
    "http://localhost:8000/api/search/",
    json={
        "query": "What is the user's job?",
        "limit": 10
    }
)

print(results.json())`}
            </pre>
            <button className="copy-button">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2" strokeWidth="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" strokeWidth="2"/>
              </svg>
              Copy
            </button>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section id="use-cases" className="use-cases">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Built for developers, used across industries</h2>
            <p className="section-subtitle">One solution, unlimited possibilities</p>
          </div>
          <div className="use-cases-grid">
            <UseCaseCard
              icon={<ChatIcon />}
              title="AI Chatbots"
              description="Enable chatbots to remember context and build relationships between conversations over time"
            />
            <UseCaseCard
              icon={<BookIcon />}
              title="Knowledge Bases"
              description="Transform documents into searchable knowledge graphs with semantic understanding"
            />
            <UseCaseCard
              icon={<EducationIcon />}
              title="Educational Platforms"
              description="Help students connect concepts through semantic relationships and learning paths"
            />
            <UseCaseCard
              icon={<MedicalIcon />}
              title="Healthcare Systems"
              description="Track patient information evolution and medical relationships with full audit trails"
            />
            <UseCaseCard
              icon={<SupportIcon />}
              title="Customer Support"
              description="Remember customer preferences, interaction history, and build personalized experiences"
            />
            <UseCaseCard
              icon={<ResearchIcon />}
              title="Research Tools"
              description="Build knowledge graphs from research papers, documents, and scholarly articles"
            />
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="stats">
        <div className="container">
          <div className="stats-grid">
            <StatCard number="239+" label="Embedding Dimensions" />
            <StatCard number="<400ms" label="Average Latency" />
            <StatCard number="3" label="Relationship Types" />
            <StatCard number="∞" label="Scalability" />
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="pricing">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Open Source & Free Forever</h2>
            <p className="section-subtitle">
              Self-hosted solution with full source code access. No per-minute charges, no usage limits.
            </p>
          </div>
          <div className="pricing-card">
            <div className="pricing-header">
              <h3>Self-Hosted</h3>
              <div className="price">$0<span className="price-period">/month</span></div>
              <p className="price-note">100% free, forever</p>
            </div>
            <ul className="pricing-features">
              <li><CheckIcon /> Unlimited memories</li>
              <li><CheckIcon /> Full source code access</li>
              <li><CheckIcon /> All features included</li>
              <li><CheckIcon /> Community support</li>
              <li><CheckIcon /> Completely customizable</li>
              <li><CheckIcon /> No API rate limits</li>
            </ul>
            <Link to="/dashboard" className="btn-primary large">Get Started</Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="container">
          <h2 className="cta-title">Start building your AI memory system today</h2>
          <p className="cta-subtitle">Join developers building intelligent memory layers for AI applications</p>
          <div className="cta-buttons">
            <Link to="/dashboard" className="btn-primary large">Get Started for Free</Link>
            <a href="https://github.com/Hamzakhan7473/AI-memory-API-" target="_blank" rel="noopener noreferrer" className="btn-secondary large">View Documentation</a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#pricing">Pricing</a>
              <Link to="/dashboard">Dashboard</Link>
            </div>
            <div className="footer-section">
              <h4>Resources</h4>
              <a href="https://github.com/Hamzakhan7473/AI-memory-API-" target="_blank" rel="noopener noreferrer">GitHub</a>
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">API Docs</a>
              <a href="#demo">Quick Start</a>
            </div>
            <div className="footer-section">
              <h4>Company</h4>
              <a href="#about">About</a>
              <a href="https://github.com/Hamzakhan7473" target="_blank" rel="noopener noreferrer">Contact</a>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© 2025 AI Memory API Platform. Open source under MIT License.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Icon Components
const SemanticIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10"/>
    <path d="M12 6v6l4 2"/>
  </svg>
);

const RelationshipIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="9" cy="12" r="3"/>
    <circle cx="15" cy="12" r="3"/>
    <path d="M12 3v3M12 18v3M9 12H3M15 12h6"/>
  </svg>
);

const SpeedIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
  </svg>
);

const VisualizationIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="3" width="7" height="7"/>
    <rect x="14" y="3" width="7" height="7"/>
    <rect x="3" y="14" width="7" height="7"/>
    <rect x="14" y="14" width="7" height="7"/>
  </svg>
);

const SearchIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8"/>
    <path d="m21 21-4.35-4.35"/>
  </svg>
);

const VersionIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    <polyline points="7.5 4.21 12 6.81 16.5 4.21"/>
    <polyline points="7.5 19.79 7.5 14.6 3 12"/>
    <polyline points="21 12 16.5 14.6 16.5 19.79"/>
    <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
    <line x1="12" y1="22.08" x2="12" y2="12"/>
  </svg>
);

const ChatIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
);

const BookIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
  </svg>
);

const EducationIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
    <path d="M6 12v5c3 3 9 3 12 0v-5"/>
  </svg>
);

const MedicalIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 2v20M2 12h20"/>
    <circle cx="12" cy="12" r="10"/>
  </svg>
);

const SupportIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
  </svg>
);

const ResearchIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
    <path d="M9 7h6M9 11h6M9 15h3"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const FeatureCard = ({ icon, title, description }) => (
  <div className="feature-card">
    <div className="feature-icon">{icon}</div>
    <h3>{title}</h3>
    <p>{description}</p>
  </div>
);

const UseCaseCard = ({ icon, title, description }) => (
  <div className="use-case-card">
    <div className="use-case-icon">{icon}</div>
    <h3>{title}</h3>
    <p>{description}</p>
  </div>
);

const StatCard = ({ number, label }) => (
  <div className="stat-card">
    <div className="stat-number">{number}</div>
    <div className="stat-label">{label}</div>
  </div>
);

export default LandingPage;
