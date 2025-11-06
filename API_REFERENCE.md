# API Endpoint Reference

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints (except `/auth/register` and `/auth/login`) require authentication:

**Bearer Token**:
```http
Authorization: Bearer <access_token>
```

**API Key**:
```http
X-API-Key: <api_key>
```

---

## Memory Management

### Create Memory
```http
POST /memories
Content-Type: application/json

{
  "content": "Memory content text",
  "metadata": {
    "custom_field": "value"
  },
  "source_type": "text",
  "source_id": "source_123"
}
```

**Response**: `201 Created`
```json
{
  "id": "mem_abc123",
  "content": "Memory content text",
  "metadata": {...},
  "version": 1,
  "is_latest": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Upload PDF
```http
POST /memories/from-pdf
Content-Type: multipart/form-data

file: <PDF file>
chunk_size: 1000
overlap: 200
```

**Response**: `201 Created`
```json
{
  "memories": [
    {
      "id": "mem_001",
      "content": "Chunk 1 content...",
      "metadata": {
        "chunk_index": 0,
        "total_chunks": 5,
        "filename": "document.pdf"
      }
    }
  ],
  "total_chunks": 5
}
```

### Get Memory
```http
GET /memories/{memory_id}
```

**Response**: `200 OK`
```json
{
  "id": "mem_abc123",
  "content": "...",
  "embedding": [0.1, 0.2, ...],
  "metadata": {...},
  "version": 1,
  "is_latest": true,
  "source_type": "text",
  "source_id": "source_123",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### List Memories
```http
GET /memories?limit=100&offset=0&only_latest=true
```

**Query Parameters**:
- `limit`: Number of results (default: 100)
- `offset`: Pagination offset (default: 0)
- `only_latest`: Filter latest versions only (default: true)

### Update Memory
```http
PUT /memories/{memory_id}
Content-Type: application/json

{
  "content": "Updated content",
  "metadata": {
    "updated": true
  }
}
```

**Response**: New memory version with UPDATE relationship

### Delete Memory
```http
DELETE /memories/{memory_id}
```

**Response**: `204 No Content`

---

## Search

### Semantic Search
```http
POST /search
Content-Type: application/json

{
  "query": "What does the user work?",
  "limit": 10,
  "min_similarity": 0.7,
  "include_subgraph": true,
  "filters": {
    "source_type": "text"
  }
}
```

**Response**: `200 OK`
```json
{
  "memories": [
    {
      "memory": {
        "id": "mem_001",
        "content": "...",
        "metadata": {...}
      },
      "similarity_score": 0.92,
      "relationships": [...]
    }
  ],
  "relationships": [
    {
      "id": "rel_001",
      "source_id": "mem_001",
      "target_id": "mem_002",
      "type": "EXTEND",
      "confidence": 0.85
    }
  ],
  "query_embedding": [0.1, 0.2, ...],
  "search_time_ms": 45.2
}
```

---

## Graph Operations

### Get Graph Statistics
```http
GET /graph/stats
```

**Response**: `200 OK`
```json
{
  "total_memories": 150,
  "latest_memories": 120,
  "relationships": {
    "update": 10,
    "extend": 50,
    "derive": 30,
    "total": 90
  },
  "average_relationships_per_memory": 0.75
}
```

### Get Detailed Statistics
```http
GET /graph/stats/detailed
```

**Response**: Extended statistics with growth trends, top connected memories, etc.

### Get Memory Lineage
```http
GET /graph/lineage/{memory_id}
```

**Response**: `200 OK`
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
      "is_latest": true
    }
  ]
}
```

### Path Search
```http
POST /graph/path-search
Content-Type: application/json

{
  "source_id": "mem_001",
  "target_id": "mem_002",
  "max_hops": 3,
  "relationship_types": ["EXTEND", "DERIVE"],
  "min_confidence": 0.5
}
```

**Response**: Paths between memories

### Multi-Hop Search
```http
POST /graph/multi-hop-search
Content-Type: application/json

{
  "query": "machine learning",
  "start_memory_id": "mem_001",
  "max_hops": 2,
  "limit": 20,
  "relationship_types": ["EXTEND"]
}
```

### Derive Insights
```http
POST /graph/derive-insights?threshold=0.85
```

**Response**: Automatically created DERIVE relationships

---

## Dashboard

### Get Graph Visualization
```http
GET /dashboard/graph?limit=100&only_latest=true&relationship_types=EXTEND,DERIVE
```

**Response**: `200 OK`
```json
{
  "nodes": [
    {
      "id": "mem_001",
      "label": "User works at...",
      "content": "Full content",
      "metadata": {...},
      "type": "memory",
      "created_at": "2024-01-01T00:00:00Z",
      "is_latest": true
    }
  ],
  "edges": [
    {
      "id": "rel_001",
      "source": "mem_001",
      "target": "mem_002",
      "type": "EXTEND",
      "confidence": 0.85,
      "label": "EXTEND"
    }
  ],
  "stats": {
    "total_memories": 150,
    "latest_memories": 120,
    "total_relationships": 90
  }
}
```

### Get Memory Details
```http
GET /dashboard/memory/{memory_id}/details
```

**Response**: Memory with relationships and lineage

---

## RAG Pipeline

### RAG Query
```http
POST /rag/query
Content-Type: application/json

{
  "query": "What is machine learning?",
  "retrieval_limit": 10,
  "min_similarity": 0.7,
  "rerank": true,
  "rerank_top_k": 20,
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response**: `200 OK`
```json
{
  "answer": "Machine learning is...",
  "citations": [
    {
      "memory_id": "mem_001",
      "content": "...",
      "relevance_score": 0.92
    }
  ],
  "retrieved_memories": [...],
  "model": "gpt-4",
  "tokens_used": 450,
  "retrieval_time_ms": 120,
  "generation_time_ms": 1800,
  "total_time_ms": 1920
}
```

### Retrieve Only
```http
POST /rag/retrieve
Content-Type: application/json

{
  "query": "machine learning",
  "limit": 10,
  "min_similarity": 0.7,
  "rerank": true,
  "rerank_top_k": null
}
```

### Generate Only
```http
POST /rag/generate
Content-Type: application/json

{
  "query": "Summarize the context",
  "context": [
    "Memory 1 content",
    "Memory 2 content"
  ],
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

---

## Voice

### Speech to Text
```http
POST /voice/stt
Content-Type: multipart/form-data

audio: <audio file>
language: en  # Optional
```

**Response**: `200 OK`
```json
{
  "text": "Transcribed text",
  "language": "en",
  "confidence": 1.0
}
```

### Text to Speech
```http
POST /voice/tts
Content-Type: application/json

{
  "text": "Hello, world!",
  "voice": "alloy",
  "format": "mp3"
}
```

**Response**: `200 OK`
```json
{
  "audio": "base64_encoded_audio",
  "format": "mp3",
  "voice": "alloy",
  "text_length": 13
}
```

### Create Memory from Voice
```http
POST /voice/voice-memory
Content-Type: multipart/form-data

audio: <audio file>
language: en
```

### Voice RAG Query
```http
POST /voice/voice-rag
Content-Type: multipart/form-data

audio: <audio file>
language: en
retrieval_limit: 10
rerank: true
model: gpt-4
```

**Response**: `200 OK`
```json
{
  "query": {
    "text": "Transcribed question",
    "language": "en"
  },
  "answer": {
    "text": "Generated answer",
    "audio": "base64_encoded_audio",
    "format": "mp3"
  },
  "citations": [...],
  "metadata": {
    "tokens_used": 450,
    "total_time_ms": 2500
  }
}
```

---

## Authentication

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword"
}
```

**Response**: `201 Created`
```json
{
  "id": "user_abc123",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>
```

### Generate API Key
```http
POST /auth/api-keys
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Production API Key"
}
```

**Response**: `201 Created`
```json
{
  "api_key": "ak_xxxxx...",
  "name": "Production API Key",
  "message": "Store this API key securely. It will not be shown again."
}
```

### List API Keys
```http
GET /auth/api-keys
Authorization: Bearer <access_token>
```

---

## WebSocket Events

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws');
```

### Events

**Memory Created**:
```json
{
  "event": "memory.created",
  "data": {
    "memory_id": "mem_123",
    "content": "...",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

**Relationship Created**:
```json
{
  "event": "relationship.created",
  "data": {
    "source_id": "mem_001",
    "target_id": "mem_002",
    "type": "EXTEND",
    "confidence": 0.85
  }
}
```

**Memory Updated**:
```json
{
  "event": "memory.updated",
  "data": {
    "old_id": "mem_001",
    "new_id": "mem_002",
    "version": 2
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Invalid or missing auth |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Resource not found |
| `429` | Too Many Requests - Rate limit exceeded |
| `500` | Internal Server Error - Server error |

---

## Rate Limits

| Plan | Requests/Minute | Requests/Day |
|------|----------------|---------------|
| Free | 60 | 1,000 |
| Pro | 300 | 10,000 |
| Enterprise | Unlimited | Unlimited |

---

## Best Practices

1. **Use Pagination**: Always paginate list endpoints
2. **Cache Embeddings**: Cache generated embeddings when possible
3. **Batch Operations**: Use batch endpoints for multiple operations
4. **Error Handling**: Implement retry logic with exponential backoff
5. **Rate Limiting**: Respect rate limits and use exponential backoff

