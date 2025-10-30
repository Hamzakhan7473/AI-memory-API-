"""
Core data models for memories and relationships
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RelationshipType(str, Enum):
    """Types of relationships between memories"""
    UPDATE = "update"  # Supersedes previous information
    EXTEND = "extend"  # Adds context while retaining original
    DERIVE = "derive"  # Inferred insight based on patterns


class Memory(BaseModel):
    """Memory object with embedding and metadata"""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    is_latest: bool = True
    source_type: str = "text"  # "text" or "pdf"
    source_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "mem_123",
                "content": "User works at Supermemory as a content engineer",
                "metadata": {"confidence": 0.95, "source": "conversation"},
                "created_at": "2024-01-01T00:00:00Z",
                "is_latest": True
            }
        }


class Relationship(BaseModel):
    """Relationship between two memories"""
    id: str
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MemoryCreate(BaseModel):
    """Request model for creating a memory"""
    content: str
    metadata: Optional[Dict[str, Any]] = None
    source_type: str = "text"
    source_id: Optional[str] = None


class MemoryUpdate(BaseModel):
    """Request model for updating a memory"""
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MemorySearch(BaseModel):
    """Request model for semantic search"""
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0)
    include_subgraph: bool = True
    filters: Optional[Dict[str, Any]] = None


class MemorySearchResponse(BaseModel):
    """Response model for semantic search"""
    memories: List[Memory]
    relationships: List[Relationship]
    query_embedding: Optional[List[float]] = None
    search_time_ms: float


class GraphNode(BaseModel):
    """Node representation for graph visualization"""
    id: str
    label: str
    content: str
    type: str = "memory"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
    is_latest: bool = True


class GraphEdge(BaseModel):
    """Edge representation for graph visualization"""
    id: str
    source: str
    target: str
    type: str  # "update", "extend", "derive"
    label: str
    confidence: float


class GraphVisualization(BaseModel):
    """Complete graph visualization data"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: Dict[str, Any]

