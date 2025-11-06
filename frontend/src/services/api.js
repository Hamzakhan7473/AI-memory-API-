import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const memoryAPI = {
  // Memory CRUD
  createMemory: (data) => api.post('/memories/', data),
  getMemory: (id) => api.get(`/memories/${id}`),
  listMemories: (limit = 100, offset = 0) => 
    api.get('/memories/', { params: { limit, offset } }),
  updateMemory: (id, data) => api.put(`/memories/${id}`, data),
  deleteMemory: (id) => api.delete(`/memories/${id}`),
  
  // PDF upload
  uploadPDF: (file, chunkSize = 1000, overlap = 200) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('chunk_size', chunkSize);
    formData.append('overlap', overlap);
    return api.post('/memories/from-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  // Search
  searchMemories: (query, limit = 10, minSimilarity = 0.7, includeSubgraph = true) =>
    api.post('/search/', {
      query,
      limit,
      min_similarity: minSimilarity,
      include_subgraph: includeSubgraph,
    }),
  
  // Graph operations
  getGraphStats: () => api.get('/graph/stats'),
  getDetailedStats: () => api.get('/graph/stats/detailed'),
  getMemoryLineage: (id) => api.get(`/graph/lineage/${id}`),
  deriveInsights: (threshold = 0.85) => 
    api.post('/graph/derive-insights', null, { params: { threshold } }),
  
  // Advanced graph search
  pathSearch: (sourceId, targetId = null, maxHops = 3, relationshipTypes = null, minConfidence = 0.5) =>
    api.post('/graph/path-search', {
      source_id: sourceId,
      target_id: targetId,
      max_hops: maxHops,
      relationship_types: relationshipTypes,
      min_confidence: minConfidence,
    }),
  
  multiHopSearch: (query = null, startMemoryId = null, maxHops = 2, limit = 20, relationshipTypes = null) =>
    api.post('/graph/multi-hop-search', {
      query,
      start_memory_id: startMemoryId,
      max_hops: maxHops,
      limit,
      relationship_types: relationshipTypes,
    }),
  
  detectCommunities: (minCommunitySize = 3) =>
    api.get('/graph/community-detection', { params: { min_community_size: minCommunitySize } }),
  
  // Dashboard
  getGraphVisualization: (limit = 100, relationshipTypes = null, onlyLatest = true) =>
    api.get('/dashboard/graph', {
      params: {
        limit,
        relationship_types: relationshipTypes,
        only_latest: onlyLatest,
      },
    }),
  getMemoryDetails: (id) => api.get(`/dashboard/memory/${id}/details`),
  
  // Relationships
  createRelationship: (sourceId, targetId, relationshipType, confidence = 0.5) =>
    api.post(`/memories/${sourceId}/relationships`, null, {
      params: {
        target_id: targetId,
        relationship_type: relationshipType,
        confidence,
      },
    }),
  getRelatedMemories: (id, relationshipType = null) =>
    api.get(`/memories/${id}/related`, {
      params: relationshipType ? { relationship_type: relationshipType } : {},
    }),

  // MemMachine API Integration (proxied through FastAPI backend)
  memmachine: {
    // Sessions
    getSessions: () => api.get('/memmachine/v1/sessions'),
    
    // Memories (MemMachine format)
    createMemory: (session, episode) => 
      api.post('/memmachine/v1/memories', { session, ...episode }),
    
    searchMemories: (session, query, limit = 10) =>
      api.post('/memmachine/v1/memories/search', {
        session,
        query,
        limit,
      }),
    
    deleteMemories: (session) =>
      api.delete('/memmachine/v1/memories', { data: { session } }),
    
    // Test connection
    healthCheck: () => api.get('/memmachine/health'),
  },
};

export default api;

