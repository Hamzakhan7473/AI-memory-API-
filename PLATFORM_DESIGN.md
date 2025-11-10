# AI Memory Platform - Comprehensive Design Document

## 📋 Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [REST API Design](#rest-api-design)
4. [Semantic Memory Objects](#semantic-memory-objects)
5. [Relationship System](#relationship-system)
6. [Semantic Search Architecture](#semantic-search-architecture)
7. [Graph Visualization Dashboard](#graph-visualization-dashboard)
8. [Versioning & Lineage Tracking](#versioning--lineage-tracking)
9. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
10. [API Specifications](#api-specifications)

---

## Executive Summary

### Platform Overview
The AI Memory Platform is an enterprise-grade system designed to help engineers manage and leverage memory for AI applications. It transforms user-provided content (text, PDFs) into a dynamic knowledge graph with semantic understanding, enabling sophisticated relationship tracking, versioning, and visualization.

### Core Capabilities
- **Content Ingestion**: Natural language text and PDF documents
- **Semantic Understanding**: Vector embeddings for semantic similarity
- **Knowledge Graph**: Dynamic graph structure with relationship types
- **Versioning**: Track memory evolution over time
- **Visualization**: Real-time graph dashboard with interactive exploration
- **Search**: Semantic search with relationship-aware retrieval

### Key Technologies
- **Backend**: FastAPI (Python)
- **Graph Database**: Neo4j
- **Vector Database**: ChromaDB
- **Frontend**: React
- **Embeddings**: OpenAI / Sentence Transformers
- **Real-time**: WebSockets

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Web UI     │  │   Mobile App  │  │   API Client  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────────┐
│              API Gateway Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Auth API   │  │  Rate Limit  │  │   CORS        │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Application Layer (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Memory API   │  │  Search API   │  │  Graph API    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Dashboard API│  │  RAG API     │  │  Voice API   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Service Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Memory       │  │  PDF         │  │  Embedding    │    │
│  │ Service      │  │  Service     │  │  Service      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Graph        │  │  Search      │  │  Relationship │    │
│  │ Service      │  │  Service     │  │  Service      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Data Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Neo4j      │  │   ChromaDB    │  │   PostgreSQL │    │
│  │  (Graph)     │  │   (Vectors)   │  │  (Metadata) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐                                          │
│  │    Redis     │                                          │
│  │   (Cache)    │                                          │
│  └──────────────┘                                          │
└──────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**API Gateway Layer**
- Authentication & Authorization
- Rate Limiting
- Request/Response Transformation
- CORS Handling

**Application Layer**
- REST API Endpoints
- Request Validation
- Response Formatting
- Error Handling

**Service Layer**
- Business Logic
- Data Processing
- Relationship Inference
- Embedding Generation

**Data Layer**
- Persistent Storage
- Graph Traversal
- Vector Search
- Caching

---

## REST API Design

### API Design Principles

1. **RESTful**: Standard HTTP methods and status codes
2. **Versioned**: `/api/v1/` prefix for future compatibility
3. **Consistent**: Uniform response format across all endpoints
4. **Documented**: OpenAPI/Swagger documentation
5. **Authenticated**: JWT or API key authentication

### API Endpoint Structure

```
/api/v1/
├── /memories          # Memory CRUD operations
├── /search            # Semantic search
├── /graph             # Graph operations
├── /dashboard         # Dashboard data
├── /rag               # RAG pipeline
└── /voice             # Voice operations
```

### Standard Response Format

```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123",
    "version": "v1"
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "MEMORY_NOT_FOUND",
    "message": "Memory with ID 'mem_123' not found",
    "details": { ... }
  },
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123"
  }
}
```

---

## Semantic Memory Objects

### Memory Object Schema

```python
class Memory:
    id: str                    # Unique identifier (mem_xxx)
    content: str               # Memory content text
    embedding: List[float]    # Vector embedding (384/1536 dim)
    metadata: Dict[str, Any]   # Flexible metadata (JSON)
    
    # Graph Properties
    source_type: str           # "text" | "pdf" | "voice"
    source_id: str             # Source document ID
    version: int               # Version number
    is_latest: bool            # Is this the latest version?
    
    # Temporal Properties
    created_at: datetime       # Creation timestamp
    updated_at: datetime       # Last update timestamp
    
    # Relationships
    relationships: List[Relationship]  # Connected memories
```

### Memory Storage Strategy

**Hybrid Storage Architecture**:

1. **ChromaDB (Vector Store)**
   - Stores: `content`, `embedding`, `metadata`
   - Purpose: Semantic similarity search
   - Index: Vector similarity index

2. **Neo4j (Graph Store)**
   - Stores: `id`, `content`, `metadata`, `relationships`
   - Purpose: Relationship traversal, versioning
   - Index: Property indexes on `id`, `source_id`, `is_latest`

3. **PostgreSQL (Metadata Store)** - Optional
   - Stores: Full memory records, audit logs
   - Purpose: Analytics, reporting, backup

### Embedding Generation

**Embedding Models**:
- **Default**: Sentence Transformers (`all-MiniLM-L6-v2`, 384 dim)
- **OpenAI**: `text-embedding-3-small` (1536 dim)
- **Custom**: Configurable model support

**Embedding Process**:
```
Content → Preprocessing → Embedding Model → Vector (384/1536 dim)
```

**Preprocessing**:
- Text normalization
- Whitespace handling
- Encoding (UTF-8)

---

## Relationship System

### Relationship Types

#### 1. UPDATE Relationship
**Purpose**: Track memory evolution and updates

**Properties**:
```python
{
    "type": "UPDATE",
    "source_id": "mem_001",
    "target_id": "mem_002",
    "confidence": 1.0,
    "reason": "Content updated",
    "created_at": "2024-01-01T00:00:00Z"
}
```

**Semantics**:
- `mem_001` was updated to `mem_002`
- `mem_002.is_latest = True`, `mem_001.is_latest = False`
- Version increment: `mem_002.version = mem_001.version + 1`

**Use Cases**:
- User edits a memory
- Content correction
- Information refinement

#### 2. EXTEND Relationship
**Purpose**: Link related memories that add context

**Properties**:
```python
{
    "type": "EXTEND",
    "source_id": "mem_001",
    "target_id": "mem_002",
    "confidence": 0.85,  # Semantic similarity
    "context": "Adds additional details",
    "created_at": "2024-01-01T00:00:00Z"
}
```

**Semantics**:
- `mem_002` extends/adds context to `mem_001`
- Both memories remain `is_latest = True`
- Bidirectional relationship (can traverse both ways)

**Use Cases**:
- PDF chunk relationships
- Related concepts
- Contextual information

#### 3. DERIVE Relationship
**Purpose**: Connect memories with inferred relationships

**Properties**:
```python
{
    "type": "DERIVE",
    "source_id": "mem_001",
    "target_id": "mem_002",
    "confidence": 0.92,  # High similarity threshold
    "inference_reason": "Semantically similar",
    "created_at": "2024-01-01T00:00:00Z"
}
```

**Semantics**:
- Automatically inferred relationship
- High confidence threshold (≥0.85)
- Indicates semantic similarity

**Use Cases**:
- Automatic relationship discovery
- Similar concept detection
- Knowledge graph enrichment

### Relationship Creation Flow

```
User Input / System Event
    ↓
Determine Relationship Type
    ↓
Calculate Confidence Score
    ↓
Validate Relationship (no duplicates)
    ↓
Create Relationship in Neo4j
    ↓
Update Memory Metadata
    ↓
Notify WebSocket Clients (real-time)
```

### Relationship Inference Algorithm

**Automatic DERIVE Relationships**:
```python
for memory_a in memories:
    for memory_b in memories:
        similarity = cosine_similarity(
            memory_a.embedding,
            memory_b.embedding
        )
        if similarity >= 0.85:
            create_relationship(
                memory_a, 
                memory_b, 
                type="DERIVE",
                confidence=similarity
            )
```

---

## Semantic Search Architecture

### Search Pipeline

```
Query Text
    ↓
Generate Query Embedding
    ↓
Vector Search (ChromaDB)
    ↓
Get Top K Results (K=20)
    ↓
Optional: Reranking (Cross-encoder)
    ↓
Filter by Confidence Threshold
    ↓
Expand with Graph Relationships (optional)
    ↓
Return Ranked Results
```

### Search Modes

#### 1. Semantic Search Only
```python
POST /api/search
{
    "query": "machine learning",
    "limit": 10,
    "min_similarity": 0.7,
    "include_subgraph": false
}
```

**Returns**: Top 10 most similar memories

#### 2. Semantic Search + Graph Expansion
```python
POST /api/search
{
    "query": "machine learning",
    "limit": 10,
    "min_similarity": 0.7,
    "include_subgraph": true
}
```

**Returns**: Top 10 memories + connected memories via relationships

#### 3. Graph-Only Search
```python
POST /api/graph/multi-hop-search
{
    "start_memory_id": "mem_001",
    "max_hops": 2,
    "limit": 20
}
```

**Returns**: Memories reachable via graph traversal

### Search Optimization

**Indexing Strategy**:
- ChromaDB: Automatic vector index
- Neo4j: Property indexes on `id`, `source_id`, `is_latest`

**Caching Strategy**:
- Redis cache for frequent queries
- Cache key: `search:{query_hash}:{params}`
- TTL: 5 minutes

**Performance Targets**:
- Vector search: < 100ms
- Graph traversal: < 200ms
- Combined search: < 300ms

---

## Graph Visualization Dashboard

### Dashboard Components

#### 1. Graph Visualization
**Technology**: React Force Graph / D3.js / Cytoscape.js

**Features**:
- Interactive node positioning
- Zoom and pan
- Node selection and details
- Relationship highlighting
- Filtering by relationship type

**Visual Elements**:
- **Nodes**: Memory objects (color-coded by source type)
- **Edges**: Relationships (color-coded by type, thickness by confidence)
- **Labels**: Truncated content preview

#### 2. Memory Timeline
**Purpose**: Visualize memory evolution over time

**Features**:
- Chronological view
- Version branches
- UPDATE relationship visualization
- Timestamp filtering

#### 3. Statistics Dashboard
**Metrics**:
- Total memories
- Latest vs outdated memories
- Relationship distribution
- Source type distribution
- Average connections per memory
- Memory growth over time

#### 4. Search Interface
**Features**:
- Semantic search input
- Results list with similarity scores
- Graph expansion toggle
- Result highlighting in graph

### Real-Time Updates

**WebSocket Events**:
```javascript
// Memory Created
{
    "event": "memory.created",
    "data": {
        "memory_id": "mem_123",
        "content": "...",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}

// Relationship Created
{
    "event": "relationship.created",
    "data": {
        "source_id": "mem_001",
        "target_id": "mem_002",
        "type": "EXTEND",
        "confidence": 0.85
    }
}

// Memory Updated
{
    "event": "memory.updated",
    "data": {
        "old_id": "mem_001",
        "new_id": "mem_002",
        "version": 2
    }
}
```

**Update Strategy**:
1. Backend emits WebSocket event
2. Frontend receives event
3. Update graph visualization
4. Animate changes (fade in, highlight)
5. Update statistics

---

## Versioning & Lineage Tracking

### Versioning Model

**Version Strategy**:
- **Immutable Memory Versions**: Each update creates new memory
- **Version Numbers**: Sequential integers (1, 2, 3, ...)
- **Latest Flag**: `is_latest` boolean on each memory
- **UPDATE Chain**: Linked list via UPDATE relationships

### Memory Update Flow

```
User Updates Memory (mem_001)
    ↓
Create New Memory (mem_002)
    ↓
Set mem_002.version = mem_001.version + 1
    ↓
Set mem_001.is_latest = False
    ↓
Set mem_002.is_latest = True
    ↓
Create UPDATE Relationship (mem_001 → mem_002)
    ↓
Preserve All Relationships from mem_001
    ↓
Emit WebSocket Event
```

### Lineage Tracking

**Lineage Query**: Get all versions of a memory

```cypher
MATCH path = (start:Memory {id: $id})-[r:UPDATE*]->(end:Memory)
WHERE end.is_latest = true
RETURN nodes(path) as lineage
ORDER BY length(path) DESC
LIMIT 1
```

**Lineage Visualization**:
```
mem_001 (v1) ─UPDATE─> mem_002 (v2) ─UPDATE─> mem_003 (v3) [LATEST]
```

### Version History API

**Get Lineage**:
```http
GET /api/graph/lineage/{memory_id}
```

**Response**:
```json
{
    "lineage": [
        {
            "id": "mem_001",
            "version": 1,
            "content": "Original content",
            "created_at": "2024-01-01T00:00:00Z",
            "is_latest": false
        },
        {
            "id": "mem_002",
            "version": 2,
            "content": "Updated content",
            "created_at": "2024-01-02T00:00:00Z",
            "is_latest": false
        },
        {
            "id": "mem_003",
            "version": 3,
            "content": "Latest content",
            "created_at": "2024-01-03T00:00:00Z",
            "is_latest": true
        }
    ]
}
```

---

## Data Flow & Processing Pipeline

### Text Input Processing

```
User Input (Text)
    ↓
1. Validate Input (length, encoding)
    ↓
2. Generate Embedding
    - Preprocess text
    - Call embedding model
    - Get vector (384/1536 dim)
    ↓
3. Create Memory Object
    - Generate ID (mem_xxx)
    - Set metadata
    - Set timestamps
    ↓
4. Store in ChromaDB
    - Store embedding + content
    ↓
5. Store in Neo4j
    - Create Memory node
    - Set properties
    ↓
6. Check for Similar Memories
    - Vector search (top 5)
    - Calculate similarities
    ↓
7. Create Relationships (if similarity > threshold)
    - EXTEND or DERIVE relationships
    ↓
8. Emit WebSocket Event
    ↓
9. Return Created Memory
```

### PDF Input Processing

```
PDF Upload
    ↓
1. Extract Text
    - PDF parsing (pdfplumber/pypdf2)
    - Extract text content
    ↓
2. Chunk Text
    - Sliding window (chunk_size=1000, overlap=200)
    - Preserve context
    ↓
3. For Each Chunk:
    ↓
    3a. Generate Embedding
    3b. Create Memory Object
        - source_type: "pdf"
        - source_id: "pdf_{filename}"
        - metadata: {chunk_index, total_chunks, filename}
    3c. Store in ChromaDB
    3d. Store in Neo4j
    ↓
4. Create EXTEND Relationships
    - Between consecutive chunks
    - Based on semantic similarity
    ↓
5. Emit WebSocket Events (batch)
    ↓
6. Return Created Memories
```

### Semantic Search Flow

```
Search Query
    ↓
1. Generate Query Embedding
    ↓
2. Vector Search (ChromaDB)
    - Query with embedding
    - Get top K results (K=20)
    - Return: (memory_id, similarity_score)
    ↓
3. Optional: Reranking
    - Cross-encoder reranking
    - Rescore top results
    ↓
4. Filter by Threshold
    - Remove results < min_similarity
    ↓
5. Fetch Full Memory Objects
    - From Neo4j (using memory_ids)
    ↓
6. Optional: Graph Expansion
    - Get related memories
    - Add to results
    ↓
7. Return Ranked Results
```

---

## API Specifications

### Memory Management API

#### Create Memory
```http
POST /api/memories
Content-Type: application/json

{
    "content": "User works at Supermemory as a content engineer",
    "metadata": {
        "confidence": 0.95,
        "source": "conversation"
    },
    "source_type": "text",
    "source_id": "conv_123"
}
```

**Response**:
```json
{
    "id": "mem_abc123",
    "content": "User works at Supermemory as a content engineer",
    "embedding": [0.1, 0.2, ...],
    "metadata": {...},
    "version": 1,
    "is_latest": true,
    "created_at": "2024-01-01T00:00:00Z"
}
```

#### Upload PDF
```http
POST /api/memories/from-pdf
Content-Type: multipart/form-data

file: <PDF file>
chunk_size: 1000
overlap: 200
```

**Response**:
```json
{
    "memories": [
        {"id": "mem_001", "content": "Chunk 1", ...},
        {"id": "mem_002", "content": "Chunk 2", ...}
    ],
    "total_chunks": 2,
    "source_id": "pdf_document.pdf"
}
```

#### Update Memory
```http
PUT /api/memories/{memory_id}
Content-Type: application/json

{
    "content": "Updated content",
    "metadata": {"updated": true}
}
```

**Response**: New memory version (with UPDATE relationship)

#### Get Memory
```http
GET /api/memories/{memory_id}
```

#### List Memories
```http
GET /api/memories?limit=100&offset=0&only_latest=true
```

### Search API

#### Semantic Search
```http
POST /api/search
Content-Type: application/json

{
    "query": "What does the user work?",
    "limit": 10,
    "min_similarity": 0.7,
    "include_subgraph": true
}
```

**Response**:
```json
{
    "memories": [
        {
            "memory": {...},
            "similarity_score": 0.92,
            "relationships": [...]
        }
    ],
    "query_embedding": [0.1, 0.2, ...],
    "search_time_ms": 45.2
}
```

### Graph API

#### Get Graph Stats
```http
GET /api/graph/stats
```

#### Get Memory Lineage
```http
GET /api/graph/lineage/{memory_id}
```

#### Path Search
```http
POST /api/graph/path-search
{
    "source_id": "mem_001",
    "target_id": "mem_002",
    "max_hops": 3
}
```

#### Multi-Hop Search
```http
POST /api/graph/multi-hop-search
{
    "start_memory_id": "mem_001",
    "max_hops": 2,
    "limit": 20
}
```

### Dashboard API

#### Get Graph Visualization
```http
GET /api/dashboard/graph?limit=100&only_latest=true
```

**Response**:
```json
{
    "nodes": [
        {
            "id": "mem_001",
            "label": "User works at...",
            "content": "Full content",
            "metadata": {...},
            "type": "memory"
        }
    ],
    "edges": [
        {
            "id": "rel_001",
            "source": "mem_001",
            "target": "mem_002",
            "type": "EXTEND",
            "confidence": 0.85
        }
    ],
    "stats": {
        "total_memories": 150,
        "latest_memories": 120,
        "total_relationships": 85
    }
}
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure ✅
- [x] FastAPI backend setup
- [x] Neo4j integration
- [x] ChromaDB integration
- [x] Embedding generation
- [x] Basic memory CRUD

### Phase 2: Relationship System ✅
- [x] Relationship types (UPDATE, EXTEND, DERIVE)
- [x] Relationship creation API
- [x] Automatic relationship inference
- [x] Relationship queries

### Phase 3: Search & Retrieval ✅
- [x] Semantic search
- [x] Graph traversal
- [x] Hybrid search (vector + graph)
- [x] Reranking support

### Phase 4: Versioning ✅
- [x] Version tracking
- [x] UPDATE relationships
- [x] Lineage queries
- [x] Latest flag management

### Phase 5: Dashboard ✅
- [x] Graph visualization API
- [x] Statistics endpoints
- [x] WebSocket real-time updates
- [x] Frontend integration

### Phase 6: Advanced Features ✅
- [x] PDF processing
- [x] RAG pipeline
- [x] Voice capabilities
- [x] Enterprise authentication

### Phase 7: Enterprise Features (In Progress)
- [ ] Multi-tenancy
- [ ] Rate limiting
- [ ] Analytics dashboard
- [ ] Billing system

---

## Performance Considerations

### Scalability
- **Horizontal Scaling**: Stateless API servers
- **Database Sharding**: Neo4j clustering, ChromaDB collection sharding
- **Caching**: Redis for frequent queries
- **CDN**: Static assets and embeddings cache

### Optimization
- **Batch Processing**: Bulk memory creation
- **Async Operations**: Background embedding generation
- **Indexing**: Proper database indexes
- **Connection Pooling**: Database connection pools

### Monitoring
- **Metrics**: Request latency, error rates, throughput
- **Logging**: Structured logging (JSON)
- **Alerting**: Error rate thresholds
- **Tracing**: Distributed tracing (OpenTelemetry)

---

## Security Considerations

### Authentication
- JWT tokens with expiration
- API key authentication
- Role-based access control (RBAC)

### Data Protection
- Encryption at rest (database)
- Encryption in transit (HTTPS)
- Input validation and sanitization
- SQL injection prevention (parameterized queries)

### Access Control
- User-level data isolation
- Workspace-level permissions
- API rate limiting per user

---

## Future Enhancements

1. **Multi-Modal Support**: Images, audio, video
2. **Advanced Chunking**: Semantic, recursive, sliding window
3. **Hybrid Search**: Dense + sparse + keyword
4. **Query Understanding**: LLM-based query expansion
5. **Auto-Tagging**: Automatic metadata extraction
6. **Collaboration**: Shared workspaces, comments
7. **Export/Import**: Knowledge graph export formats
8. **Integration**: LangChain, LlamaIndex plugins

---

## Conclusion

This design document outlines a comprehensive platform for managing AI application memory with:

- ✅ RESTful API for content ingestion
- ✅ Semantic memory objects with vector embeddings
- ✅ Dynamic knowledge graph with relationship tracking
- ✅ Semantic search with graph expansion
- ✅ Real-time visualization dashboard
- ✅ Complete versioning and lineage tracking

The platform is designed to scale from prototype to enterprise, with architecture that supports horizontal scaling, caching, and monitoring.

