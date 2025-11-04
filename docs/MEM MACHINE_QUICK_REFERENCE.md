# MemMachine Quick Reference

Quick reference for MemMachine concepts and integration decisions.

## 🎯 MemMachine Core Concepts

| Concept | Description | Our Implementation |
|---------|-------------|-------------------|
| **Session** | Context container: `session_id`, `user_id`, `agent_id`, `group_id` | Add optional session fields to Memory |
| **Episode** | Memory unit with producer/recipient | Enhance Memory model with episode fields |
| **Producer** | Who created the memory (e.g., user_123) | Optional `producer` field |
| **Produced For** | Who it's for (e.g., agent_001) | Optional `produced_for` field |
| **Episode Type** | Type: message, preference, fact, etc. | Optional `episode_type` field |
| **Group ID** | Multi-tenant organization boundary | Optional `group_id` field |

## 📡 API Comparison

### MemMachine API
```bash
# Sessions
GET  /v1/sessions

# Memories with session
POST /v1/memories
{
  "session": {
    "group_id": "team_alpha",
    "agent_id": ["agent_001"],
    "user_id": ["user_123"],
    "session_id": "session_456"
  },
  "producer": "user_123",
  "produced_for": "agent_001",
  "episode_content": "User prefers dark mode",
  "episode_type": "preference"
}

# Session-scoped search
POST /v1/memories/search
{
  "session": {...},
  "query": "user preferences",
  "limit": 5
}
```

### Our Current API
```bash
# Global memory
POST /api/memories/
{
  "content": "User prefers dark mode",
  "metadata": {...}
}

# Global search
POST /api/search/
{
  "query": "user preferences",
  "limit": 10
}
```

### Proposed Integration
- ✅ Keep `/api/*` (backward compatible)
- ✅ Add `/v1/*` (MemMachine-style)
- ✅ Share service layer

## 🔄 Data Model Changes

### Before (Current)
```python
Memory:
  - id
  - content
  - embedding
  - metadata
  - relationships
```

### After (Enhanced)
```python
Memory:
  # Existing
  - id, content, embedding, metadata, relationships
  
  # New (optional)
  - session_id, user_id, agent_id, group_id
  - producer, produced_for
  - episode_type
```

## ✅ Decision Matrix

| Decision Point | Option A | Option B | Recommendation |
|---------------|----------|----------|----------------|
| **Compatibility** | Full MemMachine | Inspired | Inspired (maintain our uniqueness) |
| **API Strategy** | Migrate to `/v1/*` | Dual APIs | Dual APIs (backward compatible) |
| **Session Storage** | Properties on Memory | Separate Session nodes | Properties (start simple) |
| **Episode Model** | New Episode type | Enhance Memory | Enhance Memory (simpler) |
| **Required Fields** | Session required | Session optional | Optional (backward compatible) |

## 📋 Implementation Checklist

### Phase 1: Session Management
- [ ] Add session fields to Memory model
- [ ] Update Neo4j schema (add properties)
- [ ] Add indexes: `session_id`, `user_id`, `agent_id`, `group_id`
- [ ] Create `/v1/sessions` endpoint
- [ ] Update memory creation to accept session
- [ ] Implement session-scoped search
- [ ] Update ChromaDB queries with session filters

### Phase 2: Episode Structure
- [ ] Add `producer`, `produced_for` fields
- [ ] Add `episode_type` field
- [ ] Update API models
- [ ] Update Neo4j schema
- [ ] Add episode-based queries

### Phase 3: Multi-Agent
- [ ] Cross-agent memory queries
- [ ] Group-based filtering
- [ ] Agent-specific endpoints
- [ ] Multi-session search

### Phase 4: Docker
- [ ] Create docker-compose.yml
- [ ] Health check endpoints
- [ ] Configuration management
- [ ] Documentation

## 🔍 Key Questions for Team

1. **Priority**: What's the business priority for MemMachine alignment?
2. **Timeline**: What's the expected timeline?
3. **Compatibility**: Full compatibility or inspired implementation?
4. **Breaking Changes**: Can we introduce breaking changes?
5. **Authentication**: Do we need auth now or later?

## 🚀 Quick Start Integration

### Step 1: Enhance Memory Model
```python
# app/core/models.py
class Memory(BaseModel):
    # ... existing fields ...
    session_id: Optional[str] = None
    user_id: Optional[List[str]] = None
    agent_id: Optional[List[str]] = None
    group_id: Optional[str] = None
    producer: Optional[str] = None
    produced_for: Optional[str] = None
    episode_type: Optional[str] = None
```

### Step 2: Add Session Endpoint
```python
# app/api/sessions.py (new)
@router.get("/v1/sessions")
async def get_sessions():
    # Return all sessions
    pass
```

### Step 3: Update Memory Service
```python
# app/services/memory_service.py
def create_memory(self, content, session_id=None, ...):
    # Handle session context
    pass
```

## 📊 Performance Targets

| Metric | Target | With Sessions |
|--------|--------|---------------|
| Search Latency | <400ms | <400ms (maintain) |
| Memory Creation | <200ms | <200ms |
| Session Query | - | <100ms |

## 🔗 Resources

- **Docs**: [docs.memmachine.ai](https://docs.memmachine.ai/)
- **Q&A**: `MEM_MACHINE_QA.md`
- **Summary**: `MEM_MACHINE_INTEGRATION_SUMMARY.md`
- **README**: Updated with MemMachine section

---

**Last Updated**: [Date]
**Version**: 1.0
