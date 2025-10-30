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
  getMemoryLineage: (id) => api.get(`/graph/lineage/${id}`),
  deriveInsights: (threshold = 0.85) => 
    api.post('/graph/derive-insights', null, { params: { threshold } }),
  
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
};

export default api;

