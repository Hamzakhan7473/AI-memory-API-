# RAG Upload Issue - Fixed

## 🐛 Issue Identified

When uploading documents, RAG was not finding them because:

1. **Metadata Parsing Issue**: Tags and other list/dict metadata were stored as JSON strings in ChromaDB, but when retrieved, they weren't being parsed back to lists/dicts
2. **Similarity Threshold Too High**: Default `min_similarity=0.6` might be too high for some document matches
3. **Search Limit**: ChromaDB query was only fetching `limit` results, but we need more to filter by similarity

## ✅ Fixes Applied

### 1. Metadata Parsing Fix
**File**: `app/services/memory_service.py`

Added logic to parse nested JSON strings in metadata when retrieving memories:
```python
# Parse any nested JSON strings in metadata (tags, authors, etc.)
# These were serialized when storing in ChromaDB
parsed_metadata = {}
for key, value in metadata.items():
    if isinstance(value, str):
        # Try to parse as JSON if it looks like JSON
        if value.startswith('[') or value.startswith('{'):
            try:
                parsed_metadata[key] = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                parsed_metadata[key] = value
        else:
            parsed_metadata[key] = value
    else:
        parsed_metadata[key] = value
```

### 2. Search Similarity Threshold
**File**: `app/api/use_cases.py`

Lowered similarity threshold for knowledge base search:
```python
# Use lower similarity threshold to find uploaded documents
results = rag_service.retrieve(
    query=query,
    limit=limit,
    min_similarity=0.5,  # Lower threshold to find more results
    rerank=True
)
```

### 3. Improved Search Function
**File**: `app/services/memory_service.py`

Enhanced `search_similar_memories` to:
- Fetch more results from ChromaDB (3x limit or 50, whichever is higher)
- Filter by similarity threshold
- Return top N results after filtering

```python
# Get more results than requested to filter by similarity
search_limit = max(limit * 3, 50)

results = self.chroma.collection.query(
    query_embeddings=[query_embedding],
    n_results=search_limit,
    include=["documents", "metadatas", "distances"]
)

# Filter by similarity and return top N
for i, memory_id in enumerate(results["ids"][0]):
    distance = results["distances"][0][i]
    similarity = 1 - distance
    
    if similarity >= min_similarity:
        content = results["documents"][0][i]
        memories.append((memory_id, similarity, content))
        
        if len(memories) >= limit:
            break
```

## 🔍 Testing

Created `test_rag_upload.py` to test:
1. Document creation
2. RAG search
3. RAG query endpoint

## 📊 Expected Behavior

After fixes:
- ✅ Uploaded documents are searchable via RAG
- ✅ Metadata (tags, category) is properly parsed
- ✅ Search finds documents with lower similarity scores
- ✅ RAG queries return relevant results from uploaded documents

## 🚀 Next Steps

1. Test with actual PDF/Word uploads
2. Monitor search performance
3. Adjust similarity thresholds if needed
4. Consider adding metadata filters for better search results

