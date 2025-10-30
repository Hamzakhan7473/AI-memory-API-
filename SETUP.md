# Setup Guide

## Prerequisites

- Python 3.8+
- Node.js 16+
- Neo4j (optional, but recommended for production)
- npm or yarn

## Quick Start

1. **Run the setup script:**
   ```bash
   ./run.sh
   ```

2. **Configure environment variables:**
   Edit `.env` file with your configuration:
   ```bash
   # OpenAI API Key (optional, for better embeddings)
   OPENAI_API_KEY=your_key_here

   # Neo4j Configuration (optional for development)
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password

   # ChromaDB will use local storage by default
   CHROMA_PERSIST_DIR=./chroma_db
   ```

3. **Start the backend:**
   ```bash
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

4. **Start the frontend (in a new terminal):**
   ```bash
   cd frontend
   npm start
   ```

## Database Setup

### Neo4j (Optional for Graph Relationships)

For production or when you need graph relationship features:

1. Install Neo4j Desktop or use Docker:
   ```bash
   docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
   ```

2. Update `.env` with your Neo4j credentials

**Note:** The system will work without Neo4j for basic functionality, but graph relationships will not be stored.

### ChromaDB

ChromaDB runs locally and stores embeddings automatically. No additional setup required.

## Features

- ✅ REST API for memory CRUD operations
- ✅ PDF processing and text chunking
- ✅ Semantic search with vector embeddings
- ✅ Knowledge graph with relationships (Update, Extend, Derive)
- ✅ Interactive graph visualization dashboard
- ✅ Versioning and lineage tracking
- ✅ Real-time WebSocket updates
- ✅ Performance monitoring (<400ms target)

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Neo4j Connection Issues

If Neo4j is not available, the system will continue to work but without graph relationship features. Check logs for connection warnings.

### ChromaDB Issues

Ensure the `chroma_db` directory is writable. The system will create it automatically if it doesn't exist.

### Frontend Connection Issues

Make sure the backend is running on port 8000, or update the `proxy` setting in `frontend/package.json`.

