# AI Memory API Platform - Project Summary

## Overview

A comprehensive memory management platform for AI applications that transforms user-provided text or PDFs into a dynamic knowledge graph with semantic understanding and real-time visualization.

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async/await support
- **Vector Database**: ChromaDB for embeddings storage
- **Graph Database**: Neo4j for relationship management
- **Embeddings**: OpenAI (optional) or Sentence Transformers
- **PDF Processing**: pdfplumber and PyPDF2

### Frontend (React)
- **Framework**: React 18
- **Graph Visualization**: vis-network (vis.js)
- **Charts**: Recharts
- **Styling**: CSS modules

## Key Features Implemented

### 1. REST API ✅
- **Memory CRUD Operations**: Create, read, update, delete memories
- **PDF Processing**: Upload and chunk PDFs automatically
- **Semantic Search**: Vector-based similarity search
- **Relationship Management**: Create Update, Extend, and Derive relationships
- **Graph Operations**: Statistics, lineage tracking, insight derivation

### 2. Knowledge Graph ✅
- **Relationship Types**:
  - **Update**: Supersedes previous information, marks old memories as outdated
  - **Extend**: Adds context while retaining original memory
  - **Derive**: Infers connections based on semantic similarity
- **Versioning**: Track how memories evolve over time
- **Lineage**: Show the full version chain of memories

### 3. Semantic Search ✅
- Vector embeddings for semantic understanding
- Similarity search with configurable thresholds
- Subgraph retrieval (related memories and relationships)
- Metadata filtering support

### 4. Interactive Dashboard ✅
- **Graph Visualization**: Interactive knowledge graph with vis-network
- **Node Selection**: Click nodes to view detailed memory information
- **Relationship Visualization**: Color-coded edges by type
- **Filters**: Filter by relationship type, latest memories, and limit
- **Statistics Panel**: Graph statistics and metrics

### 5. Performance Optimizations ✅
- **Caching Service**: In-memory caching for frequently accessed data
- **Performance Middleware**: Monitor and log slow requests (>400ms)
- **Efficient Graph Traversal**: Optimized Neo4j queries
- **Batch Processing**: Support for batch operations

### 6. Real-time Updates ✅
- **WebSocket Support**: Real-time notifications for new memories and relationships
- **Live Dashboard**: Dashboard updates as new data is added
- **Connection Management**: Automatic cleanup of disconnected clients

## API Endpoints

### Memories
- `POST /api/memories/` - Create memory from text
- `POST /api/memories/from-pdf` - Create memories from PDF
- `GET /api/memories/{id}` - Get memory by ID
- `GET /api/memories/` - List memories with pagination
- `PUT /api/memories/{id}` - Update memory
- `DELETE /api/memories/{id}` - Delete memory
- `POST /api/memories/{id}/relationships` - Create relationship
- `GET /api/memories/{id}/related` - Get related memories

### Search
- `POST /api/search/` - Semantic search with subgraph retrieval

### Graph
- `GET /api/graph/stats` - Get graph statistics
- `GET /api/graph/lineage/{id}` - Get memory version lineage
- `POST /api/graph/derive-insights` - Auto-derive relationships

### Dashboard
- `GET /api/dashboard/graph` - Get graph visualization data
- `GET /api/dashboard/memory/{id}/details` - Get memory details

### WebSocket
- `WS /api/ws` - WebSocket endpoint for real-time updates

## Data Models

### Memory
- `id`: Unique identifier
- `content`: Memory text content
- `embedding`: Vector embedding (stored in ChromaDB)
- `metadata`: Key-value metadata
- `created_at`, `updated_at`: Timestamps
- `version`: Version number
- `is_latest`: Whether this is the latest version
- `source_type`: "text" or "pdf"
- `source_id`: Optional source document ID

### Relationship
- `id`: Unique identifier
- `source_id`: Source memory ID
- `target_id`: Target memory ID
- `relationship_type`: UPDATE, EXTEND, or DERIVE
- `confidence`: Confidence score (0-1)
- `metadata`: Relationship metadata
- `created_at`: Creation timestamp

## Performance Targets

- **Latency**: <400ms for search and retrieval operations
- **Throughput**: Handles concurrent requests efficiently
- **Scalability**: Supports large knowledge graphs
- **Real-time**: Sub-second updates via WebSocket

## Project Structure

```
AI_Memory_API/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core models, config, database
│   ├── middleware/       # Performance monitoring
│   ├── services/         # Business logic
│   └── main.py           # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/    # API client
│   │   └── App.js       # Main app
│   └── package.json
├── requirements.txt      # Python dependencies
├── README.md
├── SETUP.md
└── run.sh               # Setup script
```

## Next Steps & Enhancements

### Potential Improvements:
1. **Redis Caching**: Replace in-memory cache with Redis for distributed caching
2. **Batch Operations**: Add batch create/update endpoints
3. **Advanced Search**: Add hybrid search (semantic + keyword)
4. **Export/Import**: Add functionality to export/import knowledge graphs
5. **Authentication**: Add user authentication and multi-tenant support
6. **Graph Analytics**: Add more advanced graph analytics and insights
7. **Mobile Support**: Responsive design improvements
8. **Testing**: Add unit and integration tests

## Dependencies

### Backend
- FastAPI, Uvicorn
- Neo4j driver
- ChromaDB
- OpenAI (optional)
- Sentence Transformers
- pdfplumber, PyPDF2

### Frontend
- React 18
- vis-network
- Recharts
- Axios

## Getting Started

See `SETUP.md` for detailed setup instructions.

Quick start:
```bash
./run.sh
uvicorn app.main:app --reload
cd frontend && npm start
```

## License

This project is built as a demonstration of memory management for AI applications.

