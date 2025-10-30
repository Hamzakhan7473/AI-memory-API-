"""
API endpoints for dashboard visualization data
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from app.core.models import GraphVisualization, GraphNode, GraphEdge
from app.services.memory_service import memory_service
from app.core.database import get_neo4j
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/graph", response_model=GraphVisualization)
async def get_graph_visualization(
    limit: int = 100,
    relationship_types: Optional[str] = None,
    only_latest: bool = True
):
    """
    Get graph data for visualization
    """
    session = get_neo4j().get_session()
    if not session:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        # Build relationship filter
        rel_filter = ""
        if relationship_types:
            rel_types = [rt.upper().strip() for rt in relationship_types.split(",")]
            rel_filter = f":{'|'.join(rel_types)}"
        
        # Build query for nodes and edges
        latest_filter = " {is_latest: true}" if only_latest else ""
        
        query = f"""
            MATCH (m:Memory{latest_filter})-[r{rel_filter}]->(related:Memory{latest_filter})
            WITH m, r, related
            LIMIT $limit
            RETURN m, r, related
        """
        
        result = session.run(query, {"limit": limit * 2})  # Get more to account for relationships
        
        nodes_dict = {}
        edges = []
        
        for record in result:
            # Process source node
            source_node = record["m"]
            source_id = source_node["id"]
            if source_id not in nodes_dict:
                nodes_dict[source_id] = GraphNode(
                    id=source_id,
                    label=source_node["content"][:50] + "..." if len(source_node["content"]) > 50 else source_node["content"],
                    content=source_node["content"],
                    metadata=dict(source_node.get("metadata", {})),
                    created_at=source_node["created_at"],
                    is_latest=source_node.get("is_latest", True)
                )
            
            # Process target node
            target_node = record["related"]
            target_id = target_node["id"]
            if target_id not in nodes_dict:
                nodes_dict[target_id] = GraphNode(
                    id=target_id,
                    label=target_node["content"][:50] + "..." if len(target_node["content"]) > 50 else target_node["content"],
                    content=target_node["content"],
                    metadata=dict(target_node.get("metadata", {})),
                    created_at=target_node["created_at"],
                    is_latest=target_node.get("is_latest", True)
                )
            
            # Process relationship
            rel = record["r"]
            rel_type = type(rel).__name__
            edges.append(GraphEdge(
                id=rel.get("id", f"{source_id}_{target_id}"),
                source=source_id,
                target=target_id,
                type=rel_type.lower(),
                label=rel_type,
                confidence=rel.get("confidence", 0.5)
            ))
        
        # If no relationships found, get standalone nodes
        if not nodes_dict:
            query = f"""
                MATCH (m:Memory{latest_filter})
                RETURN m
                LIMIT $limit
            """
            result = session.run(query, {"limit": limit})
            
            for record in result:
                node = record["m"]
                node_id = node["id"]
                nodes_dict[node_id] = GraphNode(
                    id=node_id,
                    label=node["content"][:50] + "..." if len(node["content"]) > 50 else node["content"],
                    content=node["content"],
                    metadata=dict(node.get("metadata", {})),
                    created_at=node["created_at"],
                    is_latest=node.get("is_latest", True)
                )
        
        # Get stats
        stats = {}
        stats_result = session.run("""
            MATCH (m:Memory)
            RETURN count(m) as total_memories,
                   count(DISTINCT CASE WHEN m.is_latest THEN 1 END) as latest_memories,
                   count((m)-[]->()) as total_relationships
        """).single()
        
        if stats_result:
            stats = {
                "total_memories": stats_result["total_memories"],
                "latest_memories": stats_result["latest_memories"],
                "total_relationships": stats_result["total_relationships"]
            }
        
        return GraphVisualization(
            nodes=list(nodes_dict.values()),
            edges=edges,
            stats=stats
        )
    finally:
        session.close()


@router.get("/memory/{memory_id}/details")
async def get_memory_details(memory_id: str):
    """
    Get detailed information about a memory for dashboard display
    """
    memory = memory_service.get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Get relationships
    related = memory_service.get_related_memories(memory_id)
    
    # Get lineage
    from app.api.graph import get_memory_lineage
    lineage_data = await get_memory_lineage(memory_id)
    
    return {
        "memory": memory,
        "related_memories": related,
        "lineage": lineage_data.get("lineage", []),
        "embedding_dimension": len(memory.embedding) if memory.embedding else 0
    }

