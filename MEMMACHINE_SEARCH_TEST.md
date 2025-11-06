# MemMachine Search Integration - Testing Guide

## New Endpoints

### 1. Search Across All Use Cases
```bash
# Search all memories
curl "http://localhost:8000/api/use-cases/memmachine/search?query=machine%20learning&limit=10"

# Search specific use case
curl "http://localhost:8000/api/use-cases/memmachine/search?query=patient&use_case=healthcare&limit=5"
```

### 2. List All Sessions
```bash
curl "http://localhost:8000/api/use-cases/memmachine/sessions"
```

## Testing Checklist

### ✅ Service Enhanced
- `search_all_memories()` method added
- Handles session extraction correctly
- Filters by use case type

### ✅ Endpoints Created
- `/api/use-cases/memmachine/search` - Unified search
- `/api/use-cases/memmachine/sessions` - Session listing

### ✅ Error Handling
- Graceful degradation per session
- Continues searching other sessions if one fails
- Logs warnings for debugging

## Use Cases Supported

1. **chatbot** - Search chatbot conversations
2. **knowledge_base** - Search knowledge base documents
3. **education** - Search educational concepts
4. **healthcare** - Search healthcare records
5. **support** - Search customer support interactions
6. **research** - Search research documents

## Example Usage

### Search All Use Cases
```bash
curl "http://localhost:8000/api/use-cases/memmachine/search?query=artificial%20intelligence&limit=10"
```

### Search Knowledge Base Only
```bash
curl "http://localhost:8000/api/use-cases/memmachine/search?query=documentation&use_case=knowledge_base&limit=5"
```

### Search Healthcare Records
```bash
curl "http://localhost:8000/api/use-cases/memmachine/search?query=patient&use_case=healthcare&limit=5"
```

### List All Sessions
```bash
curl "http://localhost:8000/api/use-cases/memmachine/sessions"
```

## Response Format

### Search Response
```json
{
  "query": "machine learning",
  "results": [
    {
      "session_id": "knowledge_base_kb_document",
      "use_case": "knowledge_base",
      "content": "...",
      "metadata": {
        "title": "...",
        "type": "knowledge_base",
        "memory_id": "...",
        "source_id": "...",
        "timestamp": "..."
      },
      "memory_id": "...",
      "source_id": "...",
      "timestamp": "...",
      "type": "knowledge_base"
    }
  ],
  "total": 5,
  "use_case_filter": null
}
```

### Sessions Response
```json
{
  "total_sessions": 10,
  "sessions_by_use_case": {
    "chatbot": ["chatbot_user1_session1", ...],
    "knowledge_base": ["knowledge_base_kb_doc1", ...],
    "education": [...],
    "healthcare": [...],
    "support": [...],
    "research": [...]
  },
  "all_sessions": [...]
}
```

## Status

✅ **Enhanced MemMachine Service**: Complete
✅ **Unified Search Endpoint**: Complete
✅ **Session Listing Endpoint**: Complete
✅ **Session Extraction**: Fixed
✅ **Error Handling**: Implemented
✅ **Testing**: Ready

---

**Ready to search across all use cases!** 🚀

