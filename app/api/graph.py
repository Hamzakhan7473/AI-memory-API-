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
            WITH m, count(r) as rel_count
            RETURN avg(rel_count) as avg_rels
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
            WITH nodes(path) as nodes, relationships(path) as rels, path
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


@router.post("/path-search")
async def find_path_between_memories(search_data: dict):
    """
    Find shortest path between two memories in the graph
    """
    session = get_neo4j().get_session()
    if not session:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        source_id = search_data.get("source_id")
        target_id = search_data.get("target_id")
        max_hops = search_data.get("max_hops", 3)
        rel_types = search_data.get("relationship_types", [])
        min_confidence = search_data.get("min_confidence", 0.5)
        
        if not source_id:
            raise HTTPException(status_code=400, detail="source_id is required")
        
        # Build relationship filter
        rel_filter = ""
        if rel_types:
            rel_types_upper = [rt.upper() for rt in rel_types]
            rel_filter = f":{'|'.join(rel_types_upper)}"
        
        if target_id:
            # Find path between two specific memories
            query = f"""
                MATCH path = shortestPath((source:Memory {{id: $source_id}})-[r{rel_filter}*1..{max_hops}]->(target:Memory {{id: $target_id}}))
                WHERE ALL(rel in relationships(path) WHERE rel.confidence >= $min_confidence)
                RETURN path, length(path) as path_length
                ORDER BY path_length
                LIMIT 1
            """
            result = session.run(query, {
                "source_id": source_id,
                "target_id": target_id,
                "min_confidence": min_confidence
            })
        else:
            # Find all paths from source (exploration)
            query = f"""
                MATCH path = (source:Memory {{id: $source_id}})-[r{rel_filter}*1..{max_hops}]->(target:Memory)
                WHERE ALL(rel in relationships(path) WHERE rel.confidence >= $min_confidence)
                RETURN path, length(path) as path_length, target.id as target_id
                ORDER BY path_length
                LIMIT 50
            """
            result = session.run(query, {
                "source_id": source_id,
                "min_confidence": min_confidence
            })
        
        paths = []
        for record in result:
            path = record["path"]
            nodes = []
            edges = []
            
            for node in path.nodes:
                nodes.append({
                    "id": node["id"],
                    "content": node["content"][:100],
                    "is_latest": node.get("is_latest", True)
                })
            
            for rel in path.relationships:
                edges.append({
                    "type": type(rel).__name__.lower(),
                    "confidence": rel.get("confidence", 0.5),
                    "source": rel.start_node["id"],
                    "target": rel.end_node["id"]
                })
            
            paths.append({
                "nodes": nodes,
                "edges": edges,
                "length": record["path_length"],
                "target_id": record.get("target_id")
            })
        
        return {"paths": paths, "total_paths": len(paths)}
    finally:
        session.close()


@router.post("/multi-hop-search")
async def multi_hop_search(search_data: dict):
    """
    Multi-hop search: Start from a memory or query and traverse relationships
    """
    session = get_neo4j().get_session()
    if not session:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        query_text = search_data.get("query")
        start_id = search_data.get("start_memory_id")
        max_hops = search_data.get("max_hops", 2)
        limit = search_data.get("limit", 20)
        rel_types = search_data.get("relationship_types", [])
        
        # Build relationship filter
        rel_filter = ""
        if rel_types:
            rel_types_upper = [rt.upper() for rt in rel_types]
            rel_filter = f":{'|'.join(rel_types_upper)}"
        
        if start_id:
            # Start from specific memory and traverse
            query = f"""
                MATCH path = (start:Memory {{id: $start_id}})-[r{rel_filter}*1..{max_hops}]->(connected:Memory)
                WHERE connected.is_latest = true
                RETURN DISTINCT connected.id as memory_id,
                       connected.content as content,
                       length(path) as hop_count,
                       [rel in relationships(path) | type(rel)] as relationship_types
                ORDER BY hop_count
                LIMIT $limit
            """
            result = session.run(query, {"start_id": start_id, "limit": limit})
        elif query_text:
            # Find similar memories first, then traverse
            similar_memories = memory_service.search_similar_memories(
                query=query_text,
                limit=5,
                min_similarity=0.7
            )
            
            if not similar_memories:
                return {"memories": [], "message": "No similar memories found"}
            
            # Get connected memories from initial results
            memory_ids = [mem_id for mem_id, _, _ in similar_memories]
            
            query = f"""
                MATCH (start:Memory)
                WHERE start.id IN $memory_ids AND start.is_latest = true
                MATCH path = (start)-[r{rel_filter}*1..{max_hops}]->(connected:Memory)
                WHERE connected.is_latest = true
                RETURN DISTINCT connected.id as memory_id,
                       connected.content as content,
                       length(path) as hop_count,
                       start.id as source_id
                ORDER BY hop_count
                LIMIT $limit
            """
            result = session.run(query, {"memory_ids": memory_ids, "limit": limit})
        else:
            raise HTTPException(status_code=400, detail="Either query or start_memory_id is required")
        
        memories = []
        for record in result:
            memory = memory_service.get_memory(record["memory_id"])
            if memory:
                memory.metadata["hop_count"] = record["hop_count"]
                memory.metadata["source_id"] = record.get("source_id")
                memories.append(memory)
        
        return {
            "memories": memories,
            "total_found": len(memories),
            "max_hops": max_hops
        }
    finally:
        session.close()


@router.get("/stats/detailed")
async def get_detailed_memory_stats():
    """
    Get comprehensive memory statistics including growth, sources, and quality metrics
    """
    session = get_neo4j().get_session()
    if not session:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        # Basic stats
        total_memories = session.run("MATCH (m:Memory) RETURN count(m) as count").single()["count"]
        latest_memories = session.run("MATCH (m:Memory {is_latest: true}) RETURN count(m) as count").single()["count"]
        outdated_memories = total_memories - latest_memories
        
        # Relationship stats
        update_count = session.run("MATCH ()-[r:UPDATE]->() RETURN count(r) as count").single()["count"]
        extend_count = session.run("MATCH ()-[r:EXTEND]->() RETURN count(r) as count").single()["count"]
        derive_count = session.run("MATCH ()-[r:DERIVE]->() RETURN count(r) as count").single()["count"]
        total_relationships = update_count + extend_count + derive_count
        
        # Memory growth over time (last 30 days)
        growth_query = """
            MATCH (m:Memory)
            WHERE m.created_at >= datetime() - duration({days: 30})
            WITH date(m.created_at) as date, count(m) as count
            RETURN toString(date) as date, count
            ORDER BY date
        """
        growth_result = session.run(growth_query)
        memory_growth = [{"date": record["date"], "count": record["count"]} for record in growth_result]
        
        # Top connected memories
        top_connected_query = """
            MATCH (m:Memory {is_latest: true})
            OPTIONAL MATCH (m)-[r]->()
            WITH m, count(r) as degree
            WHERE degree > 0
            RETURN m.id as memory_id, m.content as content, degree
            ORDER BY degree DESC
            LIMIT 10
        """
        top_connected_result = session.run(top_connected_query)
        top_connected = [
            {
                "memory_id": record["memory_id"],
                "content": record["content"][:100],
                "degree": record["degree"]
            }
            for record in top_connected_result
        ]
        
        # Source distribution
        source_query = """
            MATCH (m:Memory)
            RETURN m.source_type as source_type, count(m) as count
        """
        source_result = session.run(source_query)
        source_distribution = {record["source_type"]: record["count"] for record in source_result}
        
        # Relationship strength distribution
        strength_query = """
            MATCH ()-[r]->()
            WITH r.confidence as conf
            RETURN 
                sum(CASE WHEN conf >= 0.9 THEN 1 ELSE 0 END) as very_high,
                sum(CASE WHEN conf >= 0.7 AND conf < 0.9 THEN 1 ELSE 0 END) as high,
                sum(CASE WHEN conf >= 0.5 AND conf < 0.7 THEN 1 ELSE 0 END) as medium,
                sum(CASE WHEN conf < 0.5 THEN 1 ELSE 0 END) as low
        """
        strength_result = session.run(strength_query).single()
        strength_distribution = {
            "Very High": strength_result["very_high"] if strength_result["very_high"] else 0,
            "High": strength_result["high"] if strength_result["high"] else 0,
            "Medium": strength_result["medium"] if strength_result["medium"] else 0,
            "Low": strength_result["low"] if strength_result["low"] else 0
        }
        
        # Average relationships per memory
        avg_rels = session.run("""
            MATCH (m:Memory)
            OPTIONAL MATCH (m)-[r]->()
            WITH m, count(r) as rel_count
            RETURN avg(rel_count) as avg_rels
        """).single()["avg_rels"] or 0
        
        # Memory quality metrics
        # Calculate average confidence of relationships
        avg_confidence = session.run("""
            MATCH ()-[r]->()
            RETURN avg(r.confidence) as avg_conf
        """).single()["avg_conf"] or 0
        
        # Calculate graph density (relationships / possible relationships)
        density = 0
        if total_memories > 1:
            possible_rels = total_memories * (total_memories - 1)
            density = total_relationships / possible_rels if possible_rels > 0 else 0
        
        # Temporal stats
        temporal_query = """
            MATCH (m:Memory)
            WITH m.created_at as created_at
            RETURN min(created_at) as earliest, max(created_at) as latest, count(*) as total
        """
        temporal_result = session.run(temporal_query).single()
        
        earliest = temporal_result["earliest"] if temporal_result["earliest"] else None
        latest = temporal_result["latest"] if temporal_result["latest"] else None
        
        # Handle both datetime objects and ISO format strings from Neo4j
        if earliest:
            if isinstance(earliest, str):
                earliest_str = earliest
            else:
                earliest_str = earliest.isoformat()
        else:
            earliest_str = None
            
        if latest:
            if isinstance(latest, str):
                latest_str = latest
            else:
                latest_str = latest.isoformat()
        else:
            latest_str = None
        
        # Calculate days difference
        total_days = 0
        if earliest and latest:
            if isinstance(earliest, str):
                from datetime import datetime
                earliest_dt = datetime.fromisoformat(earliest.replace('Z', '+00:00'))
                latest_dt = datetime.fromisoformat(latest.replace('Z', '+00:00'))
                total_days = (latest_dt - earliest_dt).days
            else:
                total_days = (latest - earliest).days
        
        temporal_stats = {
            "earliest_memory": earliest_str,
            "latest_memory": latest_str,
            "total_days": total_days
        }
        
        return {
            "total_memories": total_memories,
            "latest_memories": latest_memories,
            "outdated_memories": outdated_memories,
            "total_relationships": total_relationships,
            "relationships_by_type": {
                "update": update_count,
                "extend": extend_count,
                "derive": derive_count
            },
            "average_relationships_per_memory": round(avg_rels, 2),
            "memory_growth": memory_growth,
            "top_connected_memories": top_connected,
            "source_distribution": source_distribution,
            "relationship_strength_distribution": strength_distribution,
            "memory_quality_metrics": {
                "average_confidence": round(avg_confidence, 3),
                "graph_density": round(density, 6),
                "connectivity_ratio": round(total_relationships / total_memories if total_memories > 0 else 0, 2)
            },
            "temporal_stats": temporal_stats
        }
    finally:
        session.close()

