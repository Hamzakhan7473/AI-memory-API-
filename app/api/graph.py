"""
API endpoints for graph operations and analytics
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from app.core.database import get_neo4j
from app.services.memory_service import memory_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stats")
async def get_graph_stats():
    """
    Get statistics about the knowledge graph
    """
    session = get_neo4j().get_session()
    if not session:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        # Get total memories
        memory_count = session.run("MATCH (m:Memory) RETURN count(m) as count").single()["count"]
        
        # Get relationship counts by type
        update_count = session.run("MATCH ()-[r:UPDATE]->() RETURN count(r) as count").single()["count"]
        extend_count = session.run("MATCH ()-[r:EXTEND]->() RETURN count(r) as count").single()["count"]
        derive_count = session.run("MATCH ()-[r:DERIVE]->() RETURN count(r) as count").single()["count"]
        
        # Get latest memories count
        latest_count = session.run("MATCH (m:Memory {is_latest: true}) RETURN count(m) as count").single()["count"]
        
        # Get average relationships per memory
        avg_rels = session.run("""
            MATCH (m:Memory)
            OPTIONAL MATCH (m)-[r]->()
            RETURN avg(size(collect(r))) as avg_rels
        """).single()["avg_rels"] or 0
        
        return {
            "total_memories": memory_count,
            "latest_memories": latest_count,
            "relationships": {
                "update": update_count,
                "extend": extend_count,
                "derive": derive_count,
                "total": update_count + extend_count + derive_count
            },
            "average_relationships_per_memory": round(avg_rels, 2)
        }
    finally:
        session.close()


@router.get("/lineage/{memory_id}")
async def get_memory_lineage(memory_id: str):
    """
    Get the version lineage for a memory (how it evolved over time)
    """
    session = get_neo4j().get_session()
    if not session:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        # Find all versions in the lineage (following UPDATE relationships)
        result = session.run("""
            MATCH path = (start:Memory {id: $id})-[r:UPDATE*]->(end:Memory)
            WHERE end.is_latest = true
            WITH nodes(path) as nodes, relationships(path) as rels
            RETURN [n in nodes | {id: n.id, content: n.content, created_at: n.created_at, version: n.version}] as lineage
            ORDER BY length(path) DESC
            LIMIT 1
        """, {"id": memory_id})
        
        record = result.single()
        if record:
            return {"lineage": record["lineage"]}
        
        # If no UPDATE chain, return just this memory
        memory = memory_service.get_memory(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {"lineage": [{
            "id": memory.id,
            "content": memory.content,
            "created_at": memory.created_at.isoformat(),
            "version": memory.version
        }]}
    finally:
        session.close()


@router.post("/derive-insights")
async def derive_insights(threshold: float = 0.85):
    """
    Automatically derive new relationships based on semantic similarity
    """
    try:
        from app.core.models import RelationshipType
        
        # Get all latest memories
        memories = memory_service.list_memories(limit=1000)
        latest_memories = [m for m in memories if m.is_latest]
        
        derived_count = 0
        derived_relationships = []
        
        # Compare memories pairwise (optimized with caching)
        from itertools import combinations
        for mem1, mem2 in combinations(latest_memories, 2):
            if mem1.embedding and mem2.embedding:
                from app.core.embeddings import cosine_similarity
                similarity = cosine_similarity(mem1.embedding, mem2.embedding)
                
                if similarity >= threshold:
                    # Check if relationship already exists
                    existing = memory_service.get_related_memories(mem1.id)
                    if mem2.id not in [m.id for m in existing]:
                        # Create DERIVE relationship
                        rel = memory_service.create_relationship(
                            mem1.id,
                            mem2.id,
                            relationship_type=RelationshipType.DERIVE,
                            confidence=similarity
                        )
                        derived_relationships.append(rel)
                        derived_count += 1
        
        return {
            "derived_count": derived_count,
            "relationships": derived_relationships,
            "threshold_used": threshold
        }
    except Exception as e:
        logger.error(f"Error deriving insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

