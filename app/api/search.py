"""
API endpoints for semantic search
"""
from fastapi import APIRouter, HTTPException
from app.core.models import MemorySearch, MemorySearchResponse, Memory, Relationship
from app.services.memory_service import memory_service
from app.core.embeddings import get_embedding
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=MemorySearchResponse)
async def search_memories(search_data: MemorySearch):
    """
    Semantic search for memories with optional subgraph retrieval
    """
    start_time = time.time()
    
    try:
        # Perform semantic search
        similar_memories = memory_service.search_similar_memories(
            query=search_data.query,
            limit=search_data.limit,
            min_similarity=search_data.min_similarity
        )
        
        # Convert to Memory objects
        memory_ids = [mem_id for mem_id, _, _ in similar_memories]
        memories = []
        for memory_id, similarity, _ in similar_memories:
            memory = memory_service.get_memory(memory_id)
            if memory:
                # Add similarity score to metadata
                memory.metadata["search_similarity"] = similarity
                memories.append(memory)
        
        # Get relationships if subgraph is requested
        relationships = []
        if search_data.include_subgraph:
            # Get relationships for all found memories
            session = memory_service.neo4j.get_session()
            if session:
                try:
                    result = session.run("""
                        MATCH (m1:Memory)-[r]->(m2:Memory)
                        WHERE m1.id IN $memory_ids OR m2.id IN $memory_ids
                        RETURN type(r) as rel_type, 
                               r.confidence as confidence,
                               r.id as rel_id,
                               r.created_at as created_at,
                               m1.id as source_id,
                               m2.id as target_id,
                               r.metadata as metadata
                    """, {"memory_ids": memory_ids})
                    
                    for record in result:
                        relationships.append(Relationship(
                            id=record.get("rel_id", ""),
                            source_id=record["source_id"],
                            target_id=record["target_id"],
                            relationship_type=record["rel_type"].lower(),
                            confidence=record.get("confidence", 0.5),
                            metadata=dict(record.get("metadata", {})),
                            created_at=record.get("created_at")
                        ))
                finally:
                    session.close()
        
        # Apply filters if provided
        if search_data.filters:
            filtered_memories = []
            for memory in memories:
                match = True
                for key, value in search_data.filters.items():
                    if key not in memory.metadata or memory.metadata[key] != value:
                        match = False
                        break
                if match:
                    filtered_memories.append(memory)
            memories = filtered_memories
        
        # Generate query embedding for response
        query_embedding = get_embedding(search_data.query)
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return MemorySearchResponse(
            memories=memories,
            relationships=relationships,
            query_embedding=query_embedding,
            search_time_ms=search_time
        )
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

