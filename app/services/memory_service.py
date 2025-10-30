"""
Memory service for CRUD operations and relationship management
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
from app.core.models import Memory, Relationship, RelationshipType
from app.core.database import get_neo4j, get_chroma
from app.core.embeddings import get_embedding, cosine_similarity
import time

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing memories and their relationships"""
    
    def __init__(self):
        self.neo4j = get_neo4j()
        self.chroma = get_chroma()
    
    def create_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None,
                     source_type: str = "text", source_id: Optional[str] = None) -> Memory:
        """
        Create a new memory with embedding
        
        Args:
            content: Memory content
            metadata: Optional metadata dictionary
            source_type: Type of source ("text" or "pdf")
            source_id: Optional source document ID
            
        Returns:
            Created Memory object
        """
        start_time = time.time()
        
        # Generate embedding
        embedding = get_embedding(content)
        
        # Create memory ID
        memory_id = f"mem_{uuid.uuid4().hex[:12]}"
        
        # Create memory object
        memory = Memory(
            id=memory_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            source_type=source_type,
            source_id=source_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store embedding in ChromaDB
        self.chroma.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "source_type": source_type,
                "source_id": source_id or "",
                "created_at": memory.created_at.isoformat(),
                **memory.metadata
            }]
        )
        
        # Store in Neo4j graph
        session = self.neo4j.get_session()
        if session:
            try:
                session.run("""
                    CREATE (m:Memory {
                        id: $id,
                        content: $content,
                        source_type: $source_type,
                        source_id: $source_id,
                        created_at: $created_at,
                        updated_at: $updated_at,
                        version: $version,
                        is_latest: $is_latest,
                        metadata: $metadata
                    })
                """, {
                    "id": memory_id,
                    "content": content,
                    "source_type": source_type,
                    "source_id": source_id or "",
                    "created_at": memory.created_at.isoformat(),
                    "updated_at": memory.updated_at.isoformat(),
                    "version": 1,
                    "is_latest": True,
                    "metadata": memory.metadata
                })
            finally:
                session.close()
        
        logger.info(f"Created memory {memory_id} in {(time.time() - start_time)*1000:.2f}ms")
        return memory
    
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID"""
        session = self.neo4j.get_session()
        if not session:
            return None
        
        try:
            result = session.run("""
                MATCH (m:Memory {id: $id})
                RETURN m
            """, {"id": memory_id})
            
            record = result.single()
            if not record:
                return None
            
            node = record["m"]
            
            # Get embedding from ChromaDB
            chroma_result = self.chroma.collection.get(ids=[memory_id])
            embedding = None
            if chroma_result["embeddings"]:
                embedding = chroma_result["embeddings"][0]
            
            return Memory(
                id=node["id"],
                content=node["content"],
                embedding=embedding,
                metadata=dict(node.get("metadata", {})),
                created_at=datetime.fromisoformat(node["created_at"]),
                updated_at=datetime.fromisoformat(node.get("updated_at", node["created_at"])),
                version=node.get("version", 1),
                is_latest=node.get("is_latest", True),
                source_type=node.get("source_type", "text"),
                source_id=node.get("source_id")
            )
        finally:
            session.close()
    
    def update_memory(self, memory_id: str, content: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> Optional[Memory]:
        """Update an existing memory"""
        existing = self.get_memory(memory_id)
        if not existing:
            return None
        
        # Create new version if content changed
        if content and content != existing.content:
            # Mark old version as not latest
            self._mark_as_outdated(memory_id)
            
            # Create new memory with updated content
            new_memory = self.create_memory(
                content=content,
                metadata=metadata or existing.metadata,
                source_type=existing.source_type,
                source_id=existing.source_id
            )
            
            # Create UPDATE relationship
            self.create_relationship(memory_id, new_memory.id, RelationshipType.UPDATE, confidence=1.0)
            
            return new_memory
        else:
            # Just update metadata
            if metadata:
                existing.metadata.update(metadata)
            
            # Update in Neo4j
            session = self.neo4j.get_session()
            if session:
                try:
                    session.run("""
                        MATCH (m:Memory {id: $id})
                        SET m.updated_at = $updated_at,
                            m.metadata = $metadata
                    """, {
                        "id": memory_id,
                        "updated_at": datetime.utcnow().isoformat(),
                        "metadata": existing.metadata
                    })
                finally:
                    session.close()
            
            return existing
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory and its relationships"""
        session = self.neo4j.get_session()
        if not session:
            return False
        
        try:
            # Delete from Neo4j (relationships will be deleted by cascade)
            session.run("""
                MATCH (m:Memory {id: $id})
                DETACH DELETE m
            """, {"id": memory_id})
            
            # Delete from ChromaDB
            self.chroma.collection.delete(ids=[memory_id])
            
            return True
        finally:
            session.close()
    
    def create_relationship(self, source_id: str, target_id: str,
                          relationship_type: RelationshipType,
                          confidence: float = 0.5,
                          metadata: Optional[Dict[str, Any]] = None) -> Relationship:
        """
        Create a relationship between two memories
        
        Args:
            source_id: Source memory ID
            target_id: Target memory ID
            relationship_type: Type of relationship
            confidence: Confidence score
            metadata: Optional relationship metadata
            
        Returns:
            Created Relationship object
        """
        rel_id = f"rel_{uuid.uuid4().hex[:12]}"
        relationship = Relationship(
            id=rel_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            confidence=confidence,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        
        session = self.neo4j.get_session()
        if session:
            try:
                # Neo4j relationship types must be uppercase
                rel_type = relationship_type.value.upper()
                # Validate relationship type to prevent injection
                if rel_type not in ['UPDATE', 'EXTEND', 'DERIVE']:
                    raise ValueError(f"Invalid relationship type: {rel_type}")
                
                query = f"""
                    MATCH (source:Memory {{id: $source_id}})
                    MATCH (target:Memory {{id: $target_id}})
                    CREATE (source)-[r:{rel_type}] {{
                        id: $rel_id,
                        confidence: $confidence,
                        created_at: $created_at,
                        metadata: $metadata
                    }}->(target)
                """
                
                session.run(query, {
                    "source_id": source_id,
                    "target_id": target_id,
                    "rel_id": rel_id,
                    "confidence": confidence,
                    "created_at": relationship.created_at.isoformat(),
                    "metadata": relationship.metadata
                })
            finally:
                session.close()
        
        return relationship
    
    def search_similar_memories(self, query: str, limit: int = 10,
                               min_similarity: float = 0.7) -> List[tuple]:
        """
        Find similar memories using semantic search
        
        Args:
            query: Search query text
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (memory_id, similarity_score, content) tuples
        """
        # Generate query embedding
        query_embedding = get_embedding(query)
        
        # Search in ChromaDB
        results = self.chroma.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["ids"] or not results["ids"][0]:
            return []
        
        memories = []
        for i, memory_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i]
            similarity = 1 - distance  # ChromaDB returns distances, convert to similarity
            
            if similarity >= min_similarity:
                content = results["documents"][0][i]
                memories.append((memory_id, similarity, content))
        
        return memories
    
    def get_related_memories(self, memory_id: str, relationship_type: Optional[RelationshipType] = None) -> List[Memory]:
        """
        Get memories related to a given memory
        
        Args:
            memory_id: Memory ID to find relationships for
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of related Memory objects
        """
        session = self.neo4j.get_session()
        if not session:
            return []
        
        try:
            if relationship_type:
                query = f"""
                    MATCH (m:Memory {{id: $id}})-[r:{relationship_type.value.upper()}]->(related:Memory)
                    RETURN related
                """
            else:
                query = """
                    MATCH (m:Memory {id: $id})-[r]->(related:Memory)
                    RETURN related
                """
            
            result = session.run(query, {"id": memory_id})
            related_ids = [record["related"]["id"] for record in result]
            
            memories = []
            for related_id in related_ids:
                memory = self.get_memory(related_id)
                if memory:
                    memories.append(memory)
            
            return memories
        finally:
            session.close()
    
    def _mark_as_outdated(self, memory_id: str):
        """Mark a memory as not being the latest version"""
        session = self.neo4j.get_session()
        if session:
            try:
                session.run("""
                    MATCH (m:Memory {id: $id})
                    SET m.is_latest = false
                """, {"id": memory_id})
            finally:
                session.close()
    
    def list_memories(self, limit: int = 100, offset: int = 0) -> List[Memory]:
        """List all memories with pagination"""
        session = self.neo4j.get_session()
        if not session:
            return []
        
        try:
            result = session.run("""
                MATCH (m:Memory)
                RETURN m
                ORDER BY m.created_at DESC
                SKIP $offset
                LIMIT $limit
            """, {"limit": limit, "offset": offset})
            
            memories = []
            for record in result:
                node = record["m"]
                memory = self.get_memory(node["id"])
                if memory:
                    memories.append(memory)
            
            return memories
        finally:
            session.close()


# Global service instance
memory_service = MemoryService()

