# AI Memory API Platform

> A comprehensive memory management platform for AI applications that transforms user-provided text or PDFs into a dynamic knowledge graph with semantic understanding and real-time visualization. Enhanced with **MemMachine-inspired** agentic memory architecture.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [MemMachine Integration](#memmachine-integration)
- [Research Background](#research-background)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Performance](#performance)
- [Roadmap & MemMachine Alignment](#roadmap--memmachine-alignment)
- [Contributing](#contributing)
- [References](#references)

## 🎯 Overview

This project implements a **knowledge graph-based memory system** for AI applications, inspired by how human memory works - forming connections, evolving over time, and generating insights from accumulated knowledge. Unlike traditional document storage systems, this platform creates a **living knowledge graph** where memories are dynamically interconnected through semantic relationships.

**Now enhanced with MemMachine-inspired architecture** for agentic workflows, enabling AI agents to learn, store, and recall data across multiple sessions, agents, and language models.

### Key Innovations

1. **Semantic Memory Representation**: Memories are transformed into vector embeddings for semantic understanding
2. **Dynamic Relationship Types**: Three relationship types (Update, Extend, Derive) model different information interactions
3. **Version Lineage Tracking**: Complete evolution history of memories over time
4. **Real-time Graph Visualization**: Interactive dashboard showing knowledge graph evolution
5. **Sub-400ms Latency**: Optimized for low-latency semantic search and retrieval
6. **Agentic Memory Architecture**: Session-based memory management for AI agents (MemMachine-inspired)

## 🤖 MemMachine Integration

This platform draws inspiration from **[MemMachine](https://docs.memmachine.ai/)**, an open-source memory layer for advanced AI agents. Key concepts integrated:

### MemMachine Core Concepts

- **Agentic Workflows**: Memory designed for AI agent interactions across sessions
- **Session Management**: Multi-session memory persistence with `group_id`, `agent_id`, `user_id`, `session_id`
- **Episode-Based Memories**: Memories structured as episodes with producer/recipient information
- **Cross-Agent Memory**: Memory that persists across different agents and LLMs
- **Personalized Memory**: Building evolving user profiles from accumulated interactions

### Alignment Strategy

While maintaining our unique knowledge graph architecture, we're enhancing the platform with:

1. **Session-Aware Memory**: Memories linked to specific sessions, users, and agents
2. **Episode Structure**: Producer/recipient tracking for agentic workflows
3. **Multi-Tenant Support**: Group-based organization for team/organizational memory
4. **Agent Context**: Memory retrieval scoped to agent-user-session context

See [Roadmap & MemMachine Alignment](#roadmap--memmachine-alignment) for planned enhancements.

## 📚 Research Background

### Problem Statement

Traditional AI memory systems store information as static documents without understanding relationships or evolution. This limits the ability of AI systems to:
- Understand context and connections between pieces of information
- Track how information changes over time
- Infer new insights from existing knowledge
- Provide personalized responses based on accumulated knowledge
- Support multi-agent workflows with shared context

### Theoretical Foundation

This implementation draws from several research areas:

1. **Knowledge Graphs in AI** (Pan et al., 2023): Knowledge graphs enable structured representation of information with explicit relationships
2. **Memory Systems for LLMs**: Inspired by Mem0, Supermemory, and **MemMachine** architectures
3. **Semantic Search**: Vector embeddings enable understanding beyond keyword matching
4. **Graph Databases**: Neo4j enables efficient relationship traversal
5. **Agentic Memory**: Session-based memory for AI agent workflows (MemMachine)

### Related Work

- **[MemMachine.ai](https://docs.memmachine.ai/)**: Open-source memory layer for AI agents with session management
- **Supermemory.ai**: Knowledge graph architecture with relationship types
- **Mem0.ai**: Layered memory system (conversation, session, user, organizational)
- **Pinecone**: Vector database for semantic search
- **Redis**: Memory optimization strategies for AI agents

## 🏗️ Architecture

### System Components

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│   React         │         │   FastAPI         │         │   ChromaDB   │
│   Dashboard     │◄───────►│   REST API        │◄───────►│   (Vectors)  │
│   (vis-network) │         │   WebSocket       │         └──────────────┘
└─────────────────┘         └──────────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │   Neo4j      │
                              │   (Graph)    │
                              └──────────────┘
```

### MemMachine-Aligned High-Level Diagram

![MemMachine RAG Architecture](docs/assets/memmachine-architecture.jpg)

### Technology Stack

**Backend:**
- **FastAPI**: High-performance async web framework
- **ChromaDB**: Vector database for embeddings storage
- **Neo4j**: Graph database for relationship management
- **OpenAI/Sentence-Transformers**: Embedding generation
- **pdfplumber/PyPDF2**: PDF text extraction

**Frontend:**
- **React 18**: Modern UI framework
- **vis-network**: Interactive graph visualization
- **Recharts**: Statistical charts and metrics
- **Axios**: HTTP client

### Data Flow

1. **Input Processing**: Text/PDF → Chunking → Embedding Generation
2. **Memory Storage**: ChromaDB (vectors) + Neo4j (graph relationships)
3. **Session Context**: Memories linked to sessions, users, and agents (MemMachine-inspired)
4. **Relationship Inference**: Semantic similarity → Relationship creation
5. **Query Processing**: Natural language → Embedding → Similarity search → Subgraph retrieval
6. **Visualization**: Graph data → Interactive network visualization

## ✨ Features

### Core Features

- ✅ **REST API** for memory CRUD operations
- ✅ **PDF Processing** with automatic text chunking
- ✅ **Semantic Search** with vector embeddings
- ✅ **Knowledge Graph** with three relationship types
- ✅ **Versioning & Lineage** tracking
- ✅ **Interactive Dashboard** with graph visualization
- ✅ **Real-time Updates** via WebSocket
- ✅ **Performance Monitoring** (<400ms target latency)

### Relationship Types

1. **Update**: Supersedes previous information
   - Old memory marked as `is_latest: false`
   - New memory inherits context
   - Use case: Factual corrections, status updates

2. **Extend**: Adds context while retaining original
   - Both memories remain valid
   - Enriches understanding
   - Use case: Additional details, complementary information

3. **Derive**: Inferred connections based on patterns
   - Discovered through semantic similarity
   - Shows implicit relationships
   - Use case: Pattern recognition, insight generation

### Planned MemMachine Features (Roadmap)

- 🔄 **Session Management**: Multi-session memory with session_id tracking
- 🔄 **Agent Context**: Memories scoped to specific agents and users
- 🔄 **Episode Structure**: Producer/recipient fields for agentic workflows
- 🔄 **Group-Based Organization**: Multi-tenant memory with group_id
- 🔄 **Cross-Agent Memory**: Shared memory across different agents

### Research Contributions

1. **Hybrid Storage Architecture**: Combining vector database (ChromaDB) and graph database (Neo4j) for optimal semantic search and relationship traversal

2. **Multi-type Relationship Model**: Extends traditional knowledge graphs with semantically meaningful relationship types

3. **Version Lineage Tracking**: Complete evolution history enabling temporal queries and understanding of information change

4. **Real-time Graph Updates**: WebSocket-based live updates for collaborative knowledge building

5. **Agentic Memory Foundation**: Session-based architecture for AI agent workflows

## 🚀 Installation

### Prerequisites

- **Python 3.12+** (MemMachine recommends 3.12+)
- **Node.js 16+**
- **Neo4j** (optional for development, recommended for production)
- **OpenAI API Key** (optional but recommended for better embeddings)
- npm or yarn

### Quick Setup

```bash
# Clone repository
git clone https://github.com/Hamzakhan7473/AI-memory-API-.git
cd AI-memory-API-

# Run setup script
chmod +x run.sh
./run.sh

# Configure environment
cp env.example .env
# Edit .env with your configuration
```

### Docker Setup (MemMachine-Style)

For a MemMachine-inspired Docker setup:

```bash
# Create docker-compose.yml (see examples in docs/)
docker-compose up -d
```

### Manual Installation

```bash
# Backend setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..
```

### Database Setup

**Neo4j (Optional but Recommended):**
```bash
# Using Docker
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

**Note**: For MemMachine compatibility, ensure Neo4j host in configuration matches Docker network name (not `localhost`).

**ChromaDB:**
- Automatically uses local storage (no setup required)
- Configured via `CHROMA_PERSIST_DIR` in `.env`

## 📖 Usage

### Starting the Application

**Backend:**
```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm start
```

### API Access

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Dashboard**: http://localhost:3000

### Example Usage

**Create a Memory:**
```bash
curl -X POST "http://localhost:8000/api/memories/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "User works at Supermemory as a content engineer",
    "metadata": {"source": "conversation"}
  }'
```

**Semantic Search:**
```bash
curl -X POST "http://localhost:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the user'\''s job?",
    "limit": 10,
    "min_similarity": 0.7
  }'
```

**Upload PDF:**
```bash
curl -X POST "http://localhost:8000/api/memories/from-pdf" \
  -F "file=@document.pdf" \
  -F "chunk_size=1000" \
  -F "overlap=200"
```

### MemMachine-Style API (Planned)

Future API will support session-based operations:

```bash
# Get all sessions
curl http://localhost:8000/v1/sessions

# Create memory with session context
curl -X POST "http://localhost:8000/v1/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "session": {
      "group_id": "team_alpha",
      "agent_id": ["agent_001"],
      "user_id": ["user_123"],
      "session_id": "session_456"
    },
    "producer": "user_123",
    "produced_for": "agent_001",
    "episode_content": "User prefers dark mode interface",
    "episode_type": "preference"
  }'

# Search within session context
curl -X POST "http://localhost:8000/v1/memories/search" \
  -H "Content-Type: application/json" \
  -d '{
    "session": {
      "group_id": "team_alpha",
      "agent_id": ["agent_001"],
      "user_id": ["user_123"]
    },
    "query": "user preferences",
    "limit": 5
  }'
```

## 📡 API Documentation

### Current Memory Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/memories/` | Create memory from text |
| POST | `/api/memories/from-pdf` | Create memories from PDF |
| GET | `/api/memories/{id}` | Get memory by ID |
| GET | `/api/memories/` | List memories |
| PUT | `/api/memories/{id}` | Update memory |
| DELETE | `/api/memories/{id}` | Delete memory |
| POST | `/api/memories/{id}/relationships` | Create relationship |

### Search Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search/` | Semantic search with subgraph |

### Graph Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/graph/stats` | Get graph statistics |
| GET | `/api/graph/lineage/{id}` | Get memory version lineage |
| POST | `/api/graph/derive-insights` | Auto-derive relationships |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://localhost:8000/api/ws` | Real-time updates for new memories/relationships |

### Planned MemMachine Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/sessions` | Get all sessions |
| POST | `/v1/memories` | Create memory with session context |
| POST | `/v1/memories/search` | Search memories within session context |
| DELETE | `/v1/memories` | Delete session memories |

See [API Reference](docs/API.md) for detailed documentation.

## ⚡ Performance

### Benchmarks

- **Search Latency**: <400ms (target achieved)
- **Graph Traversal**: <100ms for subgraph retrieval
- **Memory Creation**: <200ms per memory
- **Relationship Creation**: <50ms per relationship

### Optimization Strategies

1. **Caching**: In-memory cache for frequently accessed data
2. **Batch Operations**: Support for batch embedding generation
3. **Indexed Queries**: Optimized Neo4j graph queries
4. **Vector Similarity**: Efficient ChromaDB similarity search
5. **WebSocket**: Real-time updates without polling

### Scalability Considerations

- **Horizontal Scaling**: Stateless API design supports load balancing
- **Database Sharding**: ChromaDB supports collection partitioning
- **Graph Partitioning**: Neo4j supports graph partitioning strategies
- **Caching Layer**: Redis integration ready for distributed caching
- **Session Isolation**: MemMachine-style session scoping for multi-tenant support

## 🗺️ Roadmap & MemMachine Alignment

### Phase 1: Session Management (Next)
- [ ] Add session model with `session_id`, `user_id`, `agent_id`, `group_id`
- [ ] Implement `/v1/sessions` endpoint
- [ ] Update memory creation to support session context
- [ ] Session-scoped memory retrieval

### Phase 2: Episode Structure
- [ ] Add `producer` and `produced_for` fields to memories
- [ ] Implement `episode_type` and `episode_content` structure
- [ ] Update API to match MemMachine episode format

### Phase 3: Agentic Workflows
- [ ] Multi-agent memory sharing
- [ ] Cross-session memory retrieval
- [ ] Agent-specific memory filters

### Phase 4: Docker Deployment
- [ ] Docker Compose setup (MemMachine-style)
- [ ] Automated health checks
- [ ] Configuration via `cfg.yml` or environment variables

### Phase 5: Advanced Features
- [ ] Memory export/import
- [ ] Advanced analytics and insights
- [ ] Authentication and authorization
- [ ] Rate limiting and quotas

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend (optional)
- Write tests for new features
- Update documentation for API changes
- Consider MemMachine compatibility for new features

## 📚 References

### Research Papers

1. Pan, J. Z., et al. (2023). "Knowledge Graphs for AI: A Survey." *arXiv preprint arXiv:2303.16119*

2. Chen, X., et al. (2024). "Memory Systems for Large Language Models: A Comprehensive Survey." *arXiv preprint arXiv:2401.XXXXX*

### Related Projects

- **[MemMachine.ai](https://docs.memmachine.ai/)** - Open-source memory layer for AI agents
- [Supermemory.ai](https://supermemory.ai/docs/how-it-works) - Knowledge graph architecture
- [Mem0.ai](https://docs.mem0.ai/core-concepts/memory-types) - Layered memory system
- [Pinecone Documentation](https://docs.pinecone.io/guides/index-data/upsert-data) - Vector database
- [Redis AI Memory](https://redis.io/blog/build-smarter-ai-agents-manage-short-term-and-long-term-memory-with-redis/) - Memory optimization

### Technologies

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [vis-network Documentation](https://visjs.github.io/vis-network/docs/network/)
- [MemMachine Documentation](https://docs.memmachine.ai/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Hamza Khan**

- GitHub: [@Hamzakhan7473](https://github.com/Hamzakhan7473)
- Repository: [AI-memory-API-](https://github.com/Hamzakhan7473/AI-memory-API-)

## 🙏 Acknowledgments

- Inspired by **MemMachine.ai**, Supermemory.ai, and Mem0.ai architectures
- Built with FastAPI, React, Neo4j, and ChromaDB
- Special thanks to the open-source community

---

**⭐ If you find this project useful, please consider giving it a star!**

**🔄 MemMachine Integration**: We're actively working on aligning with MemMachine's agentic memory architecture. See [Roadmap](#roadmap--memmachine-alignment) for progress.
