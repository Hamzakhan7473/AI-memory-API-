"""
API endpoints for domain-specific use cases
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.services.memory_service import memory_service
from app.core.models import RelationshipType
from app.services.rag_service import rag_service
from app.services.cache_service import cache_service
from app.services.document_service import DocumentService
from app.services.memmachine_service import memmachine_service
from app.core.database import get_neo4j
from app.core.embeddings import get_embeddings
import logging
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


# Request Models
class ChatbotMessage(BaseModel):
    """Chatbot conversation message"""
    user_id: str
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class KnowledgeBaseDocument(BaseModel):
    """Knowledge base document"""
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class EducationalConcept(BaseModel):
    """Educational concept"""
    concept_name: str
    description: str
    category: str
    difficulty_level: Optional[str] = None
    prerequisites: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthcareRecord(BaseModel):
    """Healthcare patient record"""
    patient_id: str
    record_type: str  # examination, diagnosis, treatment, medication
    content: str
    doctor_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CustomerInteraction(BaseModel):
    """Customer support interaction"""
    customer_id: str
    interaction_type: str  # chat, email, phone, ticket
    content: str
    agent_id: Optional[str] = None
    sentiment: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ResearchDocument(BaseModel):
    """Research document"""
    title: str
    authors: Optional[List[str]] = None
    abstract: str
    content: str
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    keywords: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# ==================== AI Chatbots ====================

@router.post("/chatbots/message", response_model=dict)
async def chatbot_message(message: ChatbotMessage):
    """
    Process chatbot message with context memory
    
    Features:
    - Remember conversation context
    - Build relationships between conversations
    - Track user preferences over time
    """
    try:
        # Get conversation history from cache or database
        cache_key = f"chatbot:session:{message.session_id}"
        history = cache_service.get(cache_key) or []
        
        # Create memory for this message
        memory = memory_service.create_memory(
            content=message.message,
            metadata={
                "user_id": message.user_id,
                "session_id": message.session_id,
                "type": "chatbot_message",
                "context": message.context or {},
                "timestamp": message.context.get("timestamp") if message.context else None
            },
            source_type="chatbot",
            source_id=f"chat_{message.session_id}"
        )
        
        # Also store in MemMachine for enhanced memory capabilities
        memmachine_session_id = f"chatbot_{message.user_id}_{message.session_id}"
        try:
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "user", "content": message.message}
                ],
                metadata={
                    "user_id": message.user_id,
                    "session_id": message.session_id,
                    "type": "chatbot_message",
                    "memory_id": memory.id,
                    "timestamp": message.context.get("timestamp") if message.context else datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add memory to MemMachine: {e}")
        
        # Add to history
        history.append({
            "memory_id": memory.id,
            "message": message.message,
            "timestamp": memory.created_at.isoformat()
        })
        
        # Cache updated history
        cache_service.set(cache_key, history, ttl=3600)
        
        # Include conversation history in context for better responses
        context_query = message.message
        if history:
            # Add recent conversation context
            recent_context = "\n".join([h.get("message", "") for h in history[-5:]])
            context_query = f"Previous conversation:\n{recent_context}\n\nCurrent message: {message.message}"
        
        # Find related conversations from chatbot source_type only
        session = get_neo4j().get_session()
        chatbot_memory_ids = []
        if session:
            try:
                # Get all chatbot memory IDs
                kb_result = session.run("""
                    MATCH (m:Memory)
                    WHERE m.source_type = 'chatbot' AND m.is_latest = true
                    RETURN m.id as id
                """)
                chatbot_memory_ids = [record["id"] for record in kb_result]
            finally:
                session.close()
        
        # Search for related conversations
        similar_memories = memory_service.search_similar_memories(
            query=message.message,
            limit=20,
            min_similarity=0.3  # Lower threshold to find related conversations
        )
        
        # Filter to only chatbot conversations
        related = [
            (mem_id, sim, content) for mem_id, sim, content in similar_memories
            if mem_id in chatbot_memory_ids or not chatbot_memory_ids
        ][:5]  # Limit to top 5
        
        # Also search MemMachine for related conversations
        memmachine_related = []
        try:
            memmachine_session_id = f"chatbot_{message.user_id}_{message.session_id}"
            memmachine_results = await memmachine_service.search_memories(
                session_id=memmachine_session_id,
                query=message.message,
                limit=5,
                metadata_filter={"type": "chatbot_message"}
            )
            # Also search across all chatbot sessions for this user
            for result in memmachine_results:
                memmachine_related.append({
                    "source": "memmachine",
                    "content": result.get("content", ""),
                    "metadata": result.get("metadata", {})
                })
        except Exception as e:
            logger.warning(f"MemMachine search failed: {e}")
        
        # Use RAG to generate response with context
        try:
            rag_result = rag_service.rag_query(
                query=context_query,  # Use context-aware query
                retrieval_limit=5,
                min_similarity=0.3,  # Lower threshold to find relevant info
                rerank=True,
                model="gpt-4",
                max_tokens=500
            )
        except Exception as e:
            logger.error(f"RAG generation failed: {e}, using fallback")
            # Fallback response if RAG fails
            rag_result = {
                "answer": f"I received your message: '{message.message}'. How can I help you?",
                "citations": []
            }
        
        # Create memory for bot response to maintain full conversation context
        bot_memory = memory_service.create_memory(
            content=rag_result["answer"],
            metadata={
                "user_id": message.user_id,
                "session_id": message.session_id,
                "type": "chatbot_response",
                "responding_to": memory.id,
                "timestamp": datetime.utcnow().isoformat()
            },
            source_type="chatbot",
            source_id=f"chat_{message.session_id}"
        )
        
        # Also store bot response in MemMachine
        try:
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "assistant", "content": rag_result["answer"]}
                ],
                metadata={
                    "user_id": message.user_id,
                    "session_id": message.session_id,
                    "type": "chatbot_response",
                    "memory_id": bot_memory.id,
                    "responding_to": memory.id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add bot response to MemMachine: {e}")
        
        # Add bot response to history
        history.append({
            "memory_id": bot_memory.id,
            "message": rag_result["answer"],
            "role": "assistant",
            "timestamp": bot_memory.created_at.isoformat()
        })
        
        # Cache updated history
        cache_service.set(cache_key, history, ttl=3600)
        
        # Create relationship between user message and bot response
        memory_service.create_relationship(
            memory.id,
            bot_memory.id,
            RelationshipType.EXTEND,
            confidence=0.9,
            metadata={"type": "conversation_turn"}
        )
        
        return {
            "response": rag_result["answer"],
            "memory_id": memory.id,
            "bot_memory_id": bot_memory.id,
            "related_conversations": [
                {"memory_id": mem_id, "similarity": sim, "content": content[:100]}
                for mem_id, sim, content in related
            ],
            "citations": rag_result["citations"],
            "session_history": history[-10:]  # Last 10 messages
        }
    except Exception as e:
        logger.error(f"Error processing chatbot message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chatbots/session/{session_id}/history", response_model=dict)
async def get_chatbot_history(session_id: str):
    """Get conversation history for a session"""
    try:
        # Try cache first
        cache_key = f"chatbot:session:{session_id}"
        history = cache_service.get(cache_key) or []
        
        # Also get from database for completeness
        session = get_neo4j().get_session()
        if session:
            try:
                result = session.run("""
                    MATCH (m:Memory)
                    WHERE m.source_id = $source_id 
                      AND m.source_type = 'chatbot'
                      AND m.is_latest = true
                    RETURN m.id as id, m.content as content, m.metadata as metadata,
                           m.created_at as created_at
                    ORDER BY m.created_at ASC
                    LIMIT 100
                """, {"source_id": f"chat_{session_id}"})
                
                db_history = []
                for record in result:
                    metadata_str = record.get("metadata", "{}")
                    try:
                        if isinstance(metadata_str, str):
                            metadata = json.loads(metadata_str)
                        else:
                            metadata = dict(metadata_str) if metadata_str else {}
                    except (json.JSONDecodeError, TypeError):
                        metadata = {}
                    
                    # Determine if this is a user message or bot response
                    # User messages are stored directly, bot responses might be in metadata
                    db_history.append({
                        "memory_id": record["id"],
                        "message": record["content"],
                        "role": "user",  # Messages are stored as user messages
                        "timestamp": record.get("created_at"),
                        "metadata": metadata
                    })
                
                # Merge cache and database history, prefer cache for recent messages
                if db_history:
                    # Combine and deduplicate
                    all_history = history + db_history
                    # Remove duplicates by memory_id
                    seen_ids = set()
                    unique_history = []
                    for h in all_history:
                        mem_id = h.get("memory_id")
                        if mem_id and mem_id not in seen_ids:
                            seen_ids.add(mem_id)
                            unique_history.append(h)
                    # Sort by timestamp
                    unique_history.sort(key=lambda x: x.get("timestamp", ""))
                    history = unique_history[-50:]  # Last 50 messages
            finally:
                session.close()
        
        # Format for frontend
        formatted_history = []
        for h in history:
            formatted_history.append({
                "role": h.get("role", "user"),
                "content": h.get("message", h.get("content", "")),
                "timestamp": h.get("timestamp", ""),
                "memory_id": h.get("memory_id")
            })
        
        return {
            "session_id": session_id,
            "history": formatted_history,
            "total_messages": len(formatted_history)
        }
    except Exception as e:
        logger.error(f"Error getting chatbot history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chatbots/sessions", response_model=dict)
async def list_chatbot_sessions(limit: int = 50):
    """List all chatbot sessions"""
    try:
        session = get_neo4j().get_session()
        if not session:
            raise HTTPException(status_code=503, detail="Graph database not available")
        
        try:
            # Get unique sessions from chatbot memories
            result = session.run("""
                MATCH (m:Memory)
                WHERE m.source_type = 'chatbot' AND m.is_latest = true
                WITH m.source_id as source_id, 
                     min(m.created_at) as first_created,
                     max(m.created_at) as last_created,
                     count(m) as message_count
                WHERE source_id IS NOT NULL AND source_id <> ''
                RETURN source_id,
                       first_created,
                       last_created,
                       message_count
                ORDER BY last_created DESC
                LIMIT $limit
            """, {"limit": limit})
            
            sessions = []
            for record in result:
                source_id = record.get("source_id", "")
                # Extract session_id from source_id (format: chat_<session_id>)
                session_id = source_id.replace("chat_", "") if source_id.startswith("chat_") else source_id
                
                sessions.append({
                    "session_id": session_id,
                    "source_id": source_id,
                    "first_message": record.get("first_created"),
                    "last_message": record.get("last_created"),
                    "message_count": record.get("message_count", 0)
                })
            
            return {
                "sessions": sessions,
                "total": len(sessions)
            }
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error listing chatbot sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Knowledge Bases ====================

@router.post("/knowledge-base/document", response_model=dict)
async def create_knowledge_document(document: KnowledgeBaseDocument):
    """
    Transform document into searchable knowledge graph
    
    Features:
    - Semantic understanding
    - Automatic relationship detection
    - Category and tag organization
    """
    try:
        # Create memory from document
        source_id = f"kb_{document.title.lower().replace(' ', '_')}"
        memory = memory_service.create_memory(
            content=f"{document.title}\n\n{document.content}",
            metadata={
                "title": document.title,
                "category": document.category,
                "tags": document.tags or [],
                "type": "knowledge_base",
                **(document.metadata or {})
            },
            source_type="knowledge_base",
            source_id=source_id
        )
        
        # Also store in MemMachine
        memmachine_session_id = f"knowledge_base_{source_id}"
        try:
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "system", "content": f"{document.title}\n\n{document.content}"}
                ],
                metadata={
                    "title": document.title,
                    "category": document.category,
                    "tags": document.tags or [],
                    "type": "knowledge_base",
                    "memory_id": memory.id,
                    "source_id": source_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add knowledge base document to MemMachine: {e}")
        
        # Find related documents
        related = memory_service.search_similar_memories(
            query=document.content,
            limit=5,
            min_similarity=0.7
        )
        
        # Create EXTEND relationships to related documents
        for mem_id, similarity, _ in related:
            if similarity >= 0.75:
                memory_service.create_relationship(
                    memory.id,
                    mem_id,
                    relationship_type=RelationshipType.EXTEND,
                    confidence=similarity
                )
        
        return {
            "memory_id": memory.id,
            "document_id": memory.source_id,
            "related_documents": len(related),
            "relationships_created": len([r for r in related if r[1] >= 0.75])
        }
    except Exception as e:
        logger.error(f"Error creating knowledge document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-base/upload", response_model=dict)
async def upload_knowledge_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    chunk_size: int = Form(default=1000),
    overlap: int = Form(default=200)
):
    """
    Upload PDF or Word document to knowledge base
    
    Features:
    - Extract text from PDF/Word documents
    - Chunk and create memories
    - Build knowledge graph relationships
    """
    try:
        # Read file
        file_bytes = await file.read()
        
        # Extract text based on file type
        doc_service = DocumentService()
        text, file_type = doc_service.extract_text_from_file(file_bytes, file.filename)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from document")
        
        # Chunk the text
        chunks = doc_service.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        
        # Create memories from chunks using batch processing
        source_id = f"kb_{file.filename.lower().replace(' ', '_').replace('.', '_')}"
        
        # Generate embeddings in batch for all chunks (much faster)
        from app.core.embeddings import get_embeddings
        import uuid
        from datetime import datetime
        
        # OPTIMIZED: Use batch processing for faster uploads
        # Generate all embeddings at once (much faster than one-by-one)
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = get_embeddings(chunks)
        
        # Create all memory IDs at once
        memory_ids = [f"mem_{uuid.uuid4().hex[:12]}" for _ in chunks]
        
        # Prepare metadata for all chunks
        flat_metadata_list = []
        created_at = datetime.utcnow().isoformat()
        for i, chunk in enumerate(chunks):
            flat_metadata = {
                "source_type": "knowledge_base",
                "source_id": source_id or "",
                "created_at": created_at,
                "title": file.filename,
                "category": category or "",
                "type": "knowledge_base",
                "chunk_index": str(i),  # ChromaDB needs strings
                "total_chunks": str(len(chunks)),
                "filename": file.filename,
                "file_type": file_type
            }
            # Add tags as JSON string
            if tag_list:
                flat_metadata["tags"] = json.dumps(tag_list)
            flat_metadata_list.append(flat_metadata)
        
        # Batch add to ChromaDB (much faster than individual adds)
        logger.info(f"Batch adding {len(memory_ids)} memories to ChromaDB...")
        try:
            memory_service.chroma.collection.add(
                ids=memory_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=flat_metadata_list
            )
            logger.info(f"Successfully batch added {len(memory_ids)} memories to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to batch add memories to ChromaDB: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to store embeddings: {e}")
        
        # Store in Neo4j using batch transaction (faster than individual creates)
        session = get_neo4j().get_session()
        if session:
            try:
                # Use batch transaction for faster Neo4j writes
                metadata_json = json.dumps({
                    "title": file.filename,
                    "category": category,
                    "tags": tag_list,
                    "type": "knowledge_base",
                    "filename": file.filename,
                    "file_type": file_type
                })
                
                # Create all nodes in one transaction
                query = """
                UNWIND $memories AS mem
                CREATE (m:Memory {
                    id: mem.id,
                    content: mem.content,
                    source_type: mem.source_type,
                    source_id: mem.source_id,
                    created_at: mem.created_at,
                    updated_at: mem.updated_at,
                    version: 1,
                    is_latest: true,
                    metadata: mem.metadata
                })
                """
                
                memories_data = [
                    {
                        "id": memory_id,
                        "content": chunk,
                        "source_type": "knowledge_base",
                        "source_id": source_id or "",
                        "created_at": created_at,
                        "updated_at": created_at,
                        "metadata": json.dumps({
                            "title": file.filename,
                            "category": category,
                            "tags": tag_list,
                            "type": "knowledge_base",
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "filename": file.filename,
                            "file_type": file_type
                        })
                    }
                    for i, (memory_id, chunk) in enumerate(zip(memory_ids, chunks))
                ]
                
                session.run(query, {"memories": memories_data})
                logger.info(f"Successfully batch added {len(memory_ids)} memories to Neo4j")
            except Exception as e:
                logger.error(f"Failed to batch add memories to Neo4j: {e}")
            finally:
                session.close()
        
        # Create Memory objects for return (simplified)
        memories = [
            type('Memory', (), {
                'id': memory_id,
                'content': chunk,
                'metadata': {
                    "title": file.filename,
                    "category": category,
                    "tags": tag_list,
                    "type": "knowledge_base",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "filename": file.filename,
                    "file_type": file_type
                }
            })()
            for i, (memory_id, chunk) in enumerate(zip(memory_ids, chunks))
        ]
        
        # Skip relationship creation during upload for speed
        # Relationships can be created later via background task or on-demand
        
        # Also store in MemMachine (store full document as one memory)
        memmachine_session_id = f"knowledge_base_{source_id}"
        try:
            # Combine all chunks for MemMachine (it handles chunking internally)
            full_content = "\n\n".join(chunks)
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "system", "content": f"Document: {file.filename}\n\n{full_content}"}
                ],
                metadata={
                    "title": file.filename,
                    "category": category,
                    "tags": tag_list,
                    "type": "knowledge_base",
                    "source_id": source_id,
                    "filename": file.filename,
                    "file_type": file_type,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add knowledge base upload to MemMachine: {e}")
        
        return {
            "filename": file.filename,
            "file_type": file_type,
            "total_chunks": len(chunks),
            "memories_created": len(memories),
            "memory_ids": [m.id for m in memories],
            "source_id": source_id
        }
    except Exception as e:
        logger.error(f"Error uploading knowledge document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/list", response_model=dict)
async def list_knowledge_base_documents(limit: int = 50, offset: int = 0):
    """List all knowledge base documents (unique documents grouped by source_id)"""
    try:
        session = get_neo4j().get_session()
        if not session:
            raise HTTPException(status_code=503, detail="Graph database not available")
        
        try:
            # Get unique source_ids first, then get the first chunk of each document
            # Filter by source_type only (more reliable than metadata regex)
            result = session.run("""
                MATCH (m:Memory)
                WHERE m.source_type = 'knowledge_base' 
                  AND m.is_latest = true
                WITH m.source_id as source_id, 
                     min(m.created_at) as first_created,
                     collect(m)[0] as first_memory
                WHERE source_id IS NOT NULL AND source_id <> ''
                RETURN first_memory.id as id, 
                       first_memory.content as content, 
                       first_memory.metadata as metadata,
                       source_id,
                       first_created as created_at
                ORDER BY first_created DESC
                SKIP $offset
                LIMIT $limit
            """, {"offset": offset, "limit": limit})
            
            documents = []
            
            for record in result:
                # Parse metadata
                metadata_str = record.get("metadata", "{}")
                try:
                    if isinstance(metadata_str, str):
                        metadata = json.loads(metadata_str)
                    else:
                        metadata = dict(metadata_str) if metadata_str else {}
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
                
                source_id = record.get("source_id", "")
                if source_id:
                    # Get chunk count for this document
                    chunk_result = session.run("""
                        MATCH (m:Memory)
                        WHERE m.source_id = $source_id AND m.is_latest = true
                        RETURN count(m) as chunk_count
                    """, {"source_id": source_id})
                    
                    chunk_count = 0
                    for chunk_record in chunk_result:
                        chunk_count = chunk_record.get("chunk_count", 0)
                    
                    documents.append({
                        "id": record["id"],
                        "content": record["content"][:200] if record["content"] else "",
                        "metadata": metadata,
                        "source_id": source_id,
                        "filename": metadata.get("filename", "Unknown"),
                        "title": metadata.get("title", metadata.get("filename", "Untitled")),
                        "category": metadata.get("category"),
                        "tags": metadata.get("tags", []),
                        "chunk_count": chunk_count,
                        "file_type": metadata.get("file_type", "pdf"),
                        "created_at": record.get("created_at")
                    })
            
            return {
                "documents": documents,
                "total": len(documents),
                "offset": offset,
                "limit": limit
            }
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error listing knowledge base documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/search", response_model=dict)
async def search_knowledge_base(query: str, category: Optional[str] = None, limit: int = 10):
    """Search knowledge base with semantic understanding (knowledge_base documents only)"""
    try:
        # Use memory service to search with source_type filter
        # First, get all knowledge_base memory IDs from Neo4j
        session = get_neo4j().get_session()
        if not session:
            raise HTTPException(status_code=503, detail="Graph database not available")
        
        try:
            # Get all knowledge_base memory IDs
            kb_result = session.run("""
                MATCH (m:Memory)
                WHERE m.source_type = 'knowledge_base' AND m.is_latest = true
                RETURN m.id as id
            """)
            
            kb_memory_ids = [record["id"] for record in kb_result]
            
            if not kb_memory_ids:
                return {
                    "query": query,
                    "results": [],
                    "total": 0
                }
        finally:
            session.close()
        
        # Use memory_service directly to search with better control
        # Search with very low threshold to find all matches
        similar_memories = memory_service.search_similar_memories(
            query=query,
            limit=200,  # Get many results
            min_similarity=0.05  # Very low threshold to find matches
        )
        
        # Convert kb_memory_ids to set for faster lookup
        kb_memory_ids_set = set(kb_memory_ids)
        
        # Filter to only knowledge_base documents and get full Memory objects
        kb_results = []
        for memory_id, similarity, content in similar_memories:
            if memory_id in kb_memory_ids_set:
                memory = memory_service.get_memory(memory_id)
                if memory and memory.source_type == "knowledge_base":  # Double check
                    kb_results.append({
                        "memory": memory,
                        "similarity_score": similarity,
                        "rerank_score": None,
                        "final_score": similarity,
                        "retrieval_time_ms": 0
                    })
        
        # Group by source_id to show unique documents (not individual chunks)
        seen_source_ids = {}
        
        for r in kb_results:
            source_id = r["memory"].source_id
            if source_id:
                # If we haven't seen this document, or this result has higher similarity
                if source_id not in seen_source_ids or r["final_score"] > seen_source_ids[source_id]["similarity"]:
                    # Parse tags if they're a JSON string
                    tags = r["memory"].metadata.get("tags", [])
                    if isinstance(tags, str):
                        try:
                            tags = json.loads(tags)
                        except:
                            tags = []
                    
                    seen_source_ids[source_id] = {
                        "memory_id": r["memory"].id,
                        "title": r["memory"].metadata.get("title", r["memory"].metadata.get("filename", r["memory"].content[:50])),
                        "content": r["memory"].content[:200],
                        "similarity": r["final_score"],
                        "category": r["memory"].metadata.get("category"),
                        "tags": tags if isinstance(tags, list) else [],
                        "filename": r["memory"].metadata.get("filename"),
                        "source_id": source_id,
                        "file_type": r["memory"].metadata.get("file_type", "pdf")
                    }
        
        # Convert to list and sort by similarity
        unique_results = list(seen_source_ids.values())
        unique_results.sort(key=lambda x: x["similarity"], reverse=True)
        unique_results = unique_results[:limit]  # Limit final results
        
        # Filter by category if provided
        if category:
            unique_results = [
                r for r in unique_results
                if r.get("category") == category
            ]
        
        return {
            "query": query,
            "results": unique_results,
            "total": len(unique_results)
        }
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/graph/{source_id}", response_model=dict)
async def get_knowledge_base_graph(source_id: str):
    """Get knowledge graph for a specific document (by source_id)"""
    try:
        session = get_neo4j().get_session()
        if not session:
            raise HTTPException(status_code=503, detail="Graph database not available")
        
        try:
            # Get all nodes for this document source
            result = session.run("""
                MATCH (m:Memory)
                WHERE m.source_id = $source_id AND m.is_latest = true
                OPTIONAL MATCH (m)-[r]->(related:Memory)
                WHERE related.is_latest = true
                RETURN DISTINCT m.id as id, m.content as content, m.metadata as metadata,
                       related.id as related_id, related.content as related_content,
                       type(r) as rel_type, r.confidence as confidence
                LIMIT 50
            """, {"source_id": source_id})
            
            nodes = []
            edges = []
            node_ids = set()
            
            for record in result:
                node_id = record.get("id")
                if node_id and node_id not in node_ids:
                    node_ids.add(node_id)
                    metadata_str = record.get("metadata", "{}")
                    try:
                        if isinstance(metadata_str, str):
                            metadata = json.loads(metadata_str)
                        else:
                            metadata = dict(metadata_str) if metadata_str else {}
                    except (json.JSONDecodeError, TypeError):
                        metadata = {}
                    
                    nodes.append({
                        "id": node_id,
                        "content": record.get("content", ""),
                        "label": metadata.get("title", metadata.get("filename", record.get("content", "")[:50])),
                        "metadata": metadata
                    })
                
                related_id = record.get("related_id")
                if related_id and node_id:
                    edges.append({
                        "id": f"{node_id}_{related_id}",
                        "source": node_id,
                        "target": related_id,
                        "type": record.get("rel_type", "EXTEND"),
                        "confidence": record.get("confidence", 0.5)
                    })
            
            return {
                "source_id": source_id,
                "nodes": nodes,
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting knowledge base graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Educational Platforms ====================

@router.post("/education/concept", response_model=dict)
async def create_educational_concept(concept: EducationalConcept):
    """
    Create educational concept with learning paths
    
    Features:
    - Connect concepts through semantic relationships
    - Build learning paths
    - Track prerequisites
    """
    try:
        # Create memory for concept
        source_id = f"edu_{concept.concept_name.lower().replace(' ', '_')}"
        memory = memory_service.create_memory(
            content=f"{concept.concept_name}: {concept.description}",
            metadata={
                "concept_name": concept.concept_name,
                "category": concept.category,
                "difficulty_level": concept.difficulty_level,
                "prerequisites": concept.prerequisites or [],
                "type": "educational_concept"
            },
            source_type="education",
            source_id=source_id
        )
        
        # Also store in MemMachine
        memmachine_session_id = f"education_{source_id}"
        try:
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "system", "content": f"{concept.concept_name}: {concept.description}"}
                ],
                metadata={
                    "concept_name": concept.concept_name,
                    "category": concept.category,
                    "difficulty_level": concept.difficulty_level,
                    "prerequisites": concept.prerequisites or [],
                    "type": "educational_concept",
                    "memory_id": memory.id,
                    "source_id": source_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add educational concept to MemMachine: {e}")
        
        # Create relationships to prerequisite concepts
        if concept.prerequisites:
            for prereq in concept.prerequisites:
                # Find prerequisite concept
                prereq_results = memory_service.search_similar_memories(
                    query=prereq,
                    limit=1,
                    min_similarity=0.8
                )
                if prereq_results:
                    prereq_id = prereq_results[0][0]
                    memory_service.create_relationship(
                        prereq_id,
                        memory.id,
                        relationship_type=RelationshipType.EXTEND,
                        confidence=0.9
                    )
        
        # Find related concepts
        related = memory_service.search_similar_memories(
            query=concept.description,
            limit=5,
            min_similarity=0.7
        )
        
        # Create DERIVE relationships
        for mem_id, similarity, _ in related:
            if similarity >= 0.8:
                memory_service.create_relationship(
                    memory.id,
                    mem_id,
                    relationship_type=RelationshipType.DERIVE,
                    confidence=similarity
                )
        
        return {
            "memory_id": memory.id,
            "concept_id": memory.source_id,
            "prerequisites_linked": len(concept.prerequisites or []),
            "related_concepts": len(related)
        }
    except Exception as e:
        logger.error(f"Error creating educational concept: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/education/upload", response_model=dict)
async def upload_educational_material(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    difficulty_level: Optional[str] = Form(None),
    chunk_size: int = Form(default=1000),
    overlap: int = Form(default=200)
):
    """
    Upload educational material (PDF/Word) to educational platform
    
    Features:
    - Extract text from educational documents
    - Chunk and create concept memories
    - Build learning path relationships
    """
    try:
        # Read file
        file_bytes = await file.read()
        
        # Extract text based on file type
        doc_service = DocumentService()
        text, file_type = doc_service.extract_text_from_file(file_bytes, file.filename)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from document")
        
        # Chunk the text
        chunks = doc_service.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        
        # Extract concept name from filename
        concept_name = file.filename.replace('.pdf', '').replace('.docx', '').replace('.doc', '')
        
        # OPTIMIZED: Batch create memories from chunks (much faster)
        source_id = f"edu_{concept_name.lower().replace(' ', '_').replace('.', '_')}"
        
        # Generate all embeddings at once
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = get_embeddings(chunks)
        
        # Create all memory IDs at once
        memory_ids = [f"mem_{uuid.uuid4().hex[:12]}" for _ in chunks]
        
        # Prepare metadata for all chunks
        flat_metadata_list = []
        created_at = datetime.utcnow().isoformat()
        for i, chunk in enumerate(chunks):
            flat_metadata = {
                "source_type": "education",
                "source_id": source_id or "",
                "created_at": created_at,
                "concept_name": concept_name,
                "category": category or "General",
                "difficulty_level": difficulty_level or "",
                "type": "educational_concept",
                "chunk_index": str(i),
                "total_chunks": str(len(chunks)),
                "filename": file.filename,
                "file_type": file_type
            }
            flat_metadata_list.append(flat_metadata)
        
        # Batch add to ChromaDB
        logger.info(f"Batch adding {len(memory_ids)} memories to ChromaDB...")
        try:
            memory_service.chroma.collection.add(
                ids=memory_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=flat_metadata_list
            )
            logger.info(f"Successfully batch added {len(memory_ids)} memories to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to batch add memories to ChromaDB: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to store embeddings: {e}")
        
        # Store in Neo4j using batch transaction
        session = get_neo4j().get_session()
        if session:
            try:
                query = """
                UNWIND $memories AS mem
                CREATE (m:Memory {
                    id: mem.id,
                    content: mem.content,
                    source_type: mem.source_type,
                    source_id: mem.source_id,
                    created_at: mem.created_at,
                    updated_at: mem.updated_at,
                    version: 1,
                    is_latest: true,
                    metadata: mem.metadata
                })
                """
                
                memories_data = [
                    {
                        "id": memory_id,
                        "content": chunk,
                        "source_type": "education",
                        "source_id": source_id or "",
                        "created_at": created_at,
                        "updated_at": created_at,
                        "metadata": json.dumps({
                            "concept_name": concept_name,
                            "category": category or "General",
                            "difficulty_level": difficulty_level,
                            "type": "educational_concept",
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "filename": file.filename,
                            "file_type": file_type
                        })
                    }
                    for i, (memory_id, chunk) in enumerate(zip(memory_ids, chunks))
                ]
                
                session.run(query, {"memories": memories_data})
                logger.info(f"Successfully batch added {len(memory_ids)} memories to Neo4j")
            except Exception as e:
                logger.error(f"Failed to batch add memories to Neo4j: {e}")
            finally:
                session.close()
        
        # Create Memory objects for return
        memories = [
            type('Memory', (), {
                'id': memory_id,
                'content': chunk,
                'metadata': {
                    "concept_name": concept_name,
                    "category": category or "General",
                    "difficulty_level": difficulty_level,
                    "type": "educational_concept",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "filename": file.filename,
                    "file_type": file_type
                }
            })()
            for i, (memory_id, chunk) in enumerate(zip(memory_ids, chunks))
        ]
        
        # Skip relationship creation during upload for speed
        
        # Also store in MemMachine
        memmachine_session_id = f"education_{source_id}"
        try:
            full_content = "\n\n".join(chunks)
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "system", "content": f"Educational Material: {concept_name}\n\n{full_content}"}
                ],
                metadata={
                    "concept_name": concept_name,
                    "category": category or "General",
                    "difficulty_level": difficulty_level,
                    "type": "educational_concept",
                    "source_id": source_id,
                    "filename": file.filename,
                    "file_type": file_type,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add educational upload to MemMachine: {e}")
        
        return {
            "filename": file.filename,
            "file_type": file_type,
            "concept_name": concept_name,
            "total_chunks": len(chunks),
            "memories_created": len(memories),
            "memory_ids": [m.id for m in memories],
            "source_id": source_id
        }
    except Exception as e:
        logger.error(f"Error uploading educational material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/education/learning-path/{concept_id}", response_model=dict)
async def get_learning_path(concept_id: str):
    """Get learning path for a concept"""
    session = get_neo4j().get_session()
    if not session:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        # Find concept
        concept_result = session.run(
            "MATCH (m:Memory {source_id: $concept_id}) RETURN m.id as id",
            {"concept_id": f"edu_{concept_id}"}
        )
        concept_record = concept_result.single()
        
        if not concept_record:
            raise HTTPException(status_code=404, detail="Concept not found")
        
        concept_id = concept_record["id"]
        
        # Get prerequisites (concepts that this depends on)
        prereq_result = session.run("""
            MATCH (prereq:Memory)-[r:EXTEND]->(m:Memory {id: $id})
            WHERE prereq.metadata =~ '.*"type":"educational_concept".*'
            RETURN prereq.id as id, prereq.content as content
            ORDER BY r.confidence DESC
        """, {"id": concept_id})
        
        prerequisites = [
            {"id": record["id"], "content": record["content"][:100]}
            for record in prereq_result
        ]
        
        # Get concepts that depend on this (next steps)
        next_result = session.run("""
            MATCH (m:Memory {id: $id})-[r:EXTEND]->(next:Memory)
            WHERE next.metadata =~ '.*"type":"educational_concept".*'
            RETURN next.id as id, next.content as content
            ORDER BY r.confidence DESC
        """, {"id": concept_id})
        
        next_steps = [
            {"id": record["id"], "content": record["content"][:100]}
            for record in next_result
        ]
        
        return {
            "concept_id": concept_id,
            "prerequisites": prerequisites,
            "next_steps": next_steps,
            "path_complete": len(prerequisites) > 0 and len(next_steps) > 0
        }
    finally:
        session.close()


# ==================== Healthcare Systems ====================

@router.post("/healthcare/record", response_model=dict)
async def create_healthcare_record(record: HealthcareRecord):
    """
    Create healthcare record with full audit trail
    
    Features:
    - Track patient information evolution
    - Medical relationships with audit trails
    - Version control for medical records
    """
    try:
        # Create memory for record
        source_id = f"health_{record.patient_id}_{record.record_type}"
        memory = memory_service.create_memory(
            content=record.content,
            metadata={
                "patient_id": record.patient_id,
                "doctor_id": record.doctor_id,
                "record_type": record.record_type,
                "type": "healthcare_record",
                "audit_trail": {
                    "created_at": datetime.utcnow().isoformat(),
                    "created_by": record.doctor_id or "system"
                },
                **(record.metadata or {})
            },
            source_type="healthcare",
            source_id=source_id
        )
        
        # Also store in MemMachine
        memmachine_session_id = f"healthcare_{record.patient_id}"
        try:
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "system", "content": f"Record Type: {record.record_type}\n\n{record.content}"}
                ],
                metadata={
                    "patient_id": record.patient_id,
                    "doctor_id": record.doctor_id,
                    "record_type": record.record_type,
                    "type": "healthcare_record",
                    "memory_id": memory.id,
                    "source_id": source_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add healthcare record to MemMachine: {e}")
        
        # Find related patient records
        related = memory_service.search_similar_memories(
            query=f"patient {record.patient_id} {record.record_type}",
            limit=10,
            min_similarity=0.7
        )
        
        # Create UPDATE relationships for record evolution
        for mem_id, similarity, _ in related:
            existing_memory = memory_service.get_memory(mem_id)
            if existing_memory and existing_memory.metadata.get("patient_id") == record.patient_id:
                if existing_memory.metadata.get("record_type") == record.record_type:
                    memory_service.create_relationship(
                        mem_id,
                        memory.id,
                        relationship_type=RelationshipType.UPDATE,
                        confidence=1.0
                    )
        
        return {
            "memory_id": memory.id,
            "record_id": memory.source_id,
            "patient_id": record.patient_id,
            "related_records": len(related),
            "audit_trail": memory.metadata.get("audit_trail", {})
        }
    except Exception as e:
        logger.error(f"Error creating healthcare record: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/healthcare/upload", response_model=dict)
async def upload_healthcare_document(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    record_type: str = Form(...),  # examination, diagnosis, treatment, medication
    doctor_id: Optional[str] = Form(None),
    chunk_size: int = Form(default=1000),
    overlap: int = Form(default=200)
):
    """
    Upload healthcare document (PDF/Word) for patient
    
    Features:
    - Extract text from medical documents
    - Chunk and create patient records
    - Build medical timeline with audit trails
    """
    try:
        # Read file
        file_bytes = await file.read()
        
        # Extract text based on file type
        doc_service = DocumentService()
        text, file_type = doc_service.extract_text_from_file(file_bytes, file.filename)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from document")
        
        # Chunk the text
        chunks = doc_service.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        
        # OPTIMIZED: Batch create memories from chunks (much faster)
        source_id = f"health_{patient_id}_{record_type}"
        
        # Generate all embeddings at once
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = get_embeddings(chunks)
        
        # Create all memory IDs at once
        memory_ids = [f"mem_{uuid.uuid4().hex[:12]}" for _ in chunks]
        
        # Prepare metadata for all chunks
        flat_metadata_list = []
        created_at = datetime.utcnow().isoformat()
        audit_trail_json = json.dumps({
            "created_by": doctor_id or "system",
            "source": "file_upload"
        })
        for i, chunk in enumerate(chunks):
            flat_metadata = {
                "source_type": "healthcare",
                "source_id": source_id or "",
                "created_at": created_at,
                "patient_id": patient_id,
                "doctor_id": doctor_id or "",
                "record_type": record_type,
                "type": "healthcare_record",
                "chunk_index": str(i),
                "total_chunks": str(len(chunks)),
                "filename": file.filename,
                "file_type": file_type,
                "audit_trail": audit_trail_json
            }
            flat_metadata_list.append(flat_metadata)
        
        # Batch add to ChromaDB
        logger.info(f"Batch adding {len(memory_ids)} memories to ChromaDB...")
        try:
            memory_service.chroma.collection.add(
                ids=memory_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=flat_metadata_list
            )
            logger.info(f"Successfully batch added {len(memory_ids)} memories to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to batch add memories to ChromaDB: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to store embeddings: {e}")
        
        # Store in Neo4j using batch transaction
        session = get_neo4j().get_session()
        if session:
            try:
                query = """
                UNWIND $memories AS mem
                CREATE (m:Memory {
                    id: mem.id,
                    content: mem.content,
                    source_type: mem.source_type,
                    source_id: mem.source_id,
                    created_at: mem.created_at,
                    updated_at: mem.updated_at,
                    version: 1,
                    is_latest: true,
                    metadata: mem.metadata
                })
                """
                
                memories_data = [
                    {
                        "id": memory_id,
                        "content": chunk,
                        "source_type": "healthcare",
                        "source_id": source_id or "",
                        "created_at": created_at,
                        "updated_at": created_at,
                        "metadata": json.dumps({
                            "patient_id": patient_id,
                            "doctor_id": doctor_id,
                            "record_type": record_type,
                            "type": "healthcare_record",
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "filename": file.filename,
                            "file_type": file_type,
                            "audit_trail": {
                                "created_by": doctor_id or "system",
                                "source": "file_upload"
                            }
                        })
                    }
                    for i, (memory_id, chunk) in enumerate(zip(memory_ids, chunks))
                ]
                
                session.run(query, {"memories": memories_data})
                logger.info(f"Successfully batch added {len(memory_ids)} memories to Neo4j")
            except Exception as e:
                logger.error(f"Failed to batch add memories to Neo4j: {e}")
            finally:
                session.close()
        
        # Create Memory objects for return
        memories = [
            type('Memory', (), {
                'id': memory_id,
                'content': chunk,
                'metadata': {
                    "patient_id": patient_id,
                    "doctor_id": doctor_id,
                    "record_type": record_type,
                    "type": "healthcare_record",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "filename": file.filename,
                    "file_type": file_type,
                    "audit_trail": {
                        "created_by": doctor_id or "system",
                        "source": "file_upload"
                    }
                }
            })()
            for i, (memory_id, chunk) in enumerate(zip(memory_ids, chunks))
        ]
        
        # Skip relationship creation during upload for speed
        
        # Also store in MemMachine
        memmachine_session_id = f"healthcare_{patient_id}"
        try:
            full_content = "\n\n".join(chunks)
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "system", "content": f"Record Type: {record_type}\n\n{full_content}"}
                ],
                metadata={
                    "patient_id": patient_id,
                    "doctor_id": doctor_id,
                    "record_type": record_type,
                    "type": "healthcare_record",
                    "source_id": source_id,
                    "filename": file.filename,
                    "file_type": file_type,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add healthcare upload to MemMachine: {e}")
        
        return {
            "filename": file.filename,
            "file_type": file_type,
            "patient_id": patient_id,
            "record_type": record_type,
            "total_chunks": len(chunks),
            "memories_created": len(memories),
            "memory_ids": [m.id for m in memories],
            "source_id": source_id
        }
    except Exception as e:
        logger.error(f"Error uploading healthcare document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/healthcare/patient/{patient_id}/timeline", response_model=dict)
async def get_patient_timeline(patient_id: str):
    """Get complete timeline of patient records with audit trail"""
    session = get_neo4j().get_session()
    if not session:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        # Get all records for patient
        result = session.run("""
            MATCH (m:Memory)
            WHERE m.metadata =~ $patient_pattern
            AND m.metadata =~ '.*"type":"healthcare_record".*'
            RETURN m.id as id, m.content as content, m.metadata as metadata,
                   m.created_at as created_at
            ORDER BY m.created_at DESC
        """, {"patient_pattern": f'.*"patient_id":"{patient_id}".*'})
        
        records = []
        for record in result:
            metadata = json.loads(record["metadata"]) if isinstance(record["metadata"], str) else record["metadata"]
            records.append({
                "id": record["id"],
                "content": record["content"],
                "record_type": metadata.get("record_type"),
                "doctor_id": metadata.get("doctor_id"),
                "created_at": record["created_at"],
                "audit_trail": metadata.get("audit_trail", {})
            })
        
        return {
            "patient_id": patient_id,
            "records": records,
            "total_records": len(records),
            "record_types": list(set(r["record_type"] for r in records))
        }
    finally:
        session.close()


# ==================== Customer Support ====================

@router.post("/support/interaction", response_model=dict)
async def create_customer_interaction(interaction: CustomerInteraction):
    """
    Create customer support interaction
    
    Features:
    - Remember customer preferences
    - Track interaction history
    - Build personalized experiences
    """
    try:
        # Create memory for interaction
        source_id = f"support_{interaction.customer_id}_{interaction.interaction_type}"
        memory = memory_service.create_memory(
            content=interaction.content,
            metadata={
                "customer_id": interaction.customer_id,
                "agent_id": interaction.agent_id,
                "interaction_type": interaction.interaction_type,
                "sentiment": interaction.sentiment,
                "type": "customer_support",
                **(interaction.metadata or {})
            },
            source_type="support",
            source_id=source_id
        )
        
        # Also store in MemMachine
        memmachine_session_id = f"support_{interaction.customer_id}"
        try:
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "user" if interaction.interaction_type == "chat" else "system", 
                     "content": f"Type: {interaction.interaction_type}\n\n{interaction.content}"}
                ],
                metadata={
                    "customer_id": interaction.customer_id,
                    "agent_id": interaction.agent_id,
                    "interaction_type": interaction.interaction_type,
                    "sentiment": interaction.sentiment,
                    "type": "customer_support",
                    "memory_id": memory.id,
                    "source_id": source_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add customer interaction to MemMachine: {e}")
        
        # Find previous interactions
        previous = memory_service.search_similar_memories(
            query=f"customer {interaction.customer_id}",
            limit=10,
            min_similarity=0.6
        )
        
        # Create EXTEND relationships to previous interactions
        for mem_id, similarity, _ in previous:
            existing_memory = memory_service.get_memory(mem_id)
            if existing_memory and existing_memory.metadata.get("customer_id") == interaction.customer_id:
                memory_service.create_relationship(
                    mem_id,
                    memory.id,
                    relationship_type=RelationshipType.EXTEND,
                    confidence=0.8
                )
        
        # Extract preferences (simple keyword extraction)
        preferences = {}
        if "prefer" in interaction.content.lower() or "like" in interaction.content.lower():
            # Extract preferences from content
            preferences["extracted_from_content"] = True
        
        return {
            "memory_id": memory.id,
            "interaction_id": memory.source_id,
            "customer_id": interaction.customer_id,
            "previous_interactions": len(previous),
            "preferences": preferences
        }
    except Exception as e:
        logger.error(f"Error creating customer interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/support/customer/{customer_id}/profile", response_model=dict)
async def get_customer_profile(customer_id: str):
    """Get customer profile with preferences and history"""
    session = get_neo4j().get_session()
    if not session:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        # Get all interactions for customer
        result = session.run("""
            MATCH (m:Memory)
            WHERE m.metadata =~ $customer_pattern
            AND m.metadata =~ '.*"type":"customer_support".*'
            RETURN m.id as id, m.content as content, m.metadata as metadata,
                   m.created_at as created_at
            ORDER BY m.created_at DESC
        """, {"customer_pattern": f'.*"customer_id":"{customer_id}".*'})
        
        interactions = []
        preferences = {}
        sentiment_history = []
        
        for record in result:
            metadata = json.loads(record["metadata"]) if isinstance(record["metadata"], str) else record["metadata"]
            interactions.append({
                "id": record["id"],
                "content": record["content"][:200],
                "type": metadata.get("interaction_type"),
                "sentiment": metadata.get("sentiment"),
                "created_at": record["created_at"]
            })
            if metadata.get("sentiment"):
                sentiment_history.append(metadata["sentiment"])
        
        return {
            "customer_id": customer_id,
            "interactions": interactions,
            "total_interactions": len(interactions),
            "preferences": preferences,
            "sentiment_history": sentiment_history,
            "interaction_types": list(set(i["type"] for i in interactions))
        }
    finally:
        session.close()


# ==================== MemMachine Unified Search ====================

@router.get("/memmachine/search", response_model=dict)
async def search_memmachine_across_all_use_cases(
    query: str,
    limit: int = 20,
    use_case: Optional[str] = None  # Filter by use case: chatbot, knowledge_base, education, healthcare, support, research
):
    """
    Search MemMachine memories across all use cases
    
    Features:
    - Search across all use case memories
    - Filter by use case type
    - Returns unified results with session info
    """
    try:
        # Map use case names to session prefixes
        use_case_map = {
            "chatbot": "chatbot",
            "knowledge_base": "knowledge_base",
            "education": "education",
            "healthcare": "healthcare",
            "support": "support",
            "research": "research"
        }
        
        use_case_filter = None
        if use_case and use_case.lower() in use_case_map:
            use_case_filter = use_case_map[use_case.lower()]
        
        # Search across all MemMachine memories
        results = await memmachine_service.search_all_memories(
            query=query,
            limit=limit,
            use_case_filter=use_case_filter
        )
        
        # Format results for response
        # MemMachine returns episodes with structure:
        # {
        #   "uuid": "...",
        #   "content": "...",
        #   "timestamp": "...",
        #   "session_id": "...",
        #   "user_metadata": {...}
        # }
        formatted_results = []
        for result in results:
            # Extract content and metadata from MemMachine episode format
            content = result.get("content", "")
            
            # user_metadata might be empty dict, extract all metadata
            user_metadata = result.get("user_metadata", {}) or {}
            
            # Extract all episode fields
            episode_uuid = result.get("uuid", "")
            episode_type = result.get("episode_type", "default")
            timestamp = result.get("timestamp", "")
            group_id = result.get("group_id", "")
            producer_id = result.get("producer_id", "")
            produced_for_id = result.get("produced_for_id", "")
            session_id_from_episode = result.get("session_id", "")
            
            # Map MemMachine episode to our format
            formatted_results.append({
                "session_id": result.get("session_id", "") or session_id_from_episode,
                "use_case": result.get("use_case", "unknown"),
                "content": content,
                "metadata": {
                    **user_metadata,
                    "uuid": episode_uuid,
                    "episode_type": episode_type,
                    "timestamp": timestamp,
                    "group_id": group_id,
                    "producer_id": producer_id,
                    "produced_for_id": produced_for_id,
                    "content_type": result.get("content_type", "string")
                },
                "memory_id": user_metadata.get("memory_id") or episode_uuid,
                "source_id": user_metadata.get("source_id"),
                "timestamp": timestamp or user_metadata.get("timestamp", ""),
                "type": user_metadata.get("type")
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "total": len(formatted_results),
            "use_case_filter": use_case_filter
        }
    except Exception as e:
        logger.error(f"Error searching MemMachine across use cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memmachine/sessions", response_model=dict)
async def list_memmachine_sessions_by_use_case():
    """List all MemMachine sessions grouped by use case"""
    try:
        all_sessions = await memmachine_service.get_sessions()
        
        # Group sessions by use case
        use_cases = {
            "chatbot": [],
            "knowledge_base": [],
            "education": [],
            "healthcare": [],
            "support": [],
            "research": []
        }
        
        for session_id in all_sessions:
            if "_" in session_id:
                use_case = session_id.split("_")[0]
                if use_case in use_cases:
                    use_cases[use_case].append(session_id)
        
        return {
            "total_sessions": len(all_sessions),
            "sessions_by_use_case": use_cases,
            "all_sessions": all_sessions
        }
    except Exception as e:
        logger.error(f"Error listing MemMachine sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Research Tools ====================

@router.post("/research/document", response_model=dict)
async def create_research_document(document: ResearchDocument):
    """
    Build knowledge graph from research papers and documents
    
    Features:
    - Extract concepts from papers
    - Build relationships between papers
    - Citation tracking
    """
    try:
        # Create memory from document
        source_id = f"research_{document.doi or document.title.lower().replace(' ', '_')}"
        full_content = f"{document.title}\n\nAbstract: {document.abstract}\n\n{document.content}"
        memory = memory_service.create_memory(
            content=full_content,
            metadata={
                "title": document.title,
                "authors": document.authors or [],
                "publication_date": document.publication_date,
                "doi": document.doi,
                "keywords": document.keywords or [],
                "type": "research_document",
                **(document.metadata or {})
            },
            source_type="research",
            source_id=source_id
        )
        
        # Also store in MemMachine
        memmachine_session_id = f"research_{source_id}"
        try:
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "system", "content": full_content}
                ],
                metadata={
                    "title": document.title,
                    "authors": document.authors or [],
                    "publication_date": document.publication_date,
                    "doi": document.doi,
                    "keywords": document.keywords or [],
                    "type": "research_document",
                    "memory_id": memory.id,
                    "source_id": source_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add research document to MemMachine: {e}")
        
        # Find related papers
        related = memory_service.search_similar_memories(
            query=document.abstract,
            limit=10,
            min_similarity=0.7
        )
        
        # Create DERIVE relationships to related papers
        for mem_id, similarity, _ in related:
            existing_memory = memory_service.get_memory(mem_id)
            if existing_memory and existing_memory.metadata.get("type") == "research_document":
                memory_service.create_relationship(
                    memory.id,
                    mem_id,
                    relationship_type=RelationshipType.DERIVE,
                    confidence=similarity
                )
        
        return {
            "memory_id": memory.id,
            "document_id": memory.source_id,
            "related_papers": len(related),
            "relationships_created": len([r for r in related if r[1] >= 0.75])
        }
    except Exception as e:
        logger.error(f"Error creating research document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/upload", response_model=dict)
async def upload_research_document(
    file: UploadFile = File(...),
    authors: Optional[str] = Form(None),  # Comma-separated authors
    doi: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None),  # Comma-separated keywords
    publication_date: Optional[str] = Form(None),
    chunk_size: int = Form(default=1000),
    overlap: int = Form(default=200)
):
    """
    Upload research paper (PDF/Word) to research tools
    
    Features:
    - Extract text from research papers
    - Chunk and create memories
    - Build citation network
    """
    try:
        # Read file
        file_bytes = await file.read()
        
        # Extract text based on file type
        doc_service = DocumentService()
        text, file_type = doc_service.extract_text_from_file(file_bytes, file.filename)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from document")
        
        # Chunk the text
        chunks = doc_service.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        
        # Parse authors and keywords
        author_list = [a.strip() for a in authors.split(',')] if authors else []
        keyword_list = [k.strip() for k in keywords.split(',')] if keywords else []
        
        # Extract title from filename or first chunk
        title = file.filename.replace('.pdf', '').replace('.docx', '').replace('.doc', '')
        
        # OPTIMIZED: Batch create memories from chunks (much faster)
        source_id = f"research_{doi or title.lower().replace(' ', '_').replace('.', '_')}"
        
        # Generate all embeddings at once
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = get_embeddings(chunks)
        
        # Create all memory IDs at once
        memory_ids = [f"mem_{uuid.uuid4().hex[:12]}" for _ in chunks]
        
        # Prepare metadata for all chunks
        flat_metadata_list = []
        created_at = datetime.utcnow().isoformat()
        for i, chunk in enumerate(chunks):
            flat_metadata = {
                "source_type": "research",
                "source_id": source_id or "",
                "created_at": created_at,
                "title": title,
                "doi": doi or "",
                "publication_date": publication_date or "",
                "type": "research_document",
                "chunk_index": str(i),
                "total_chunks": str(len(chunks)),
                "filename": file.filename,
                "file_type": file_type
            }
            # Add lists as JSON strings
            if author_list:
                flat_metadata["authors"] = json.dumps(author_list)
            if keyword_list:
                flat_metadata["keywords"] = json.dumps(keyword_list)
            flat_metadata_list.append(flat_metadata)
        
        # Batch add to ChromaDB
        logger.info(f"Batch adding {len(memory_ids)} memories to ChromaDB...")
        try:
            memory_service.chroma.collection.add(
                ids=memory_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=flat_metadata_list
            )
            logger.info(f"Successfully batch added {len(memory_ids)} memories to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to batch add memories to ChromaDB: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to store embeddings: {e}")
        
        # Store in Neo4j using batch transaction
        session = get_neo4j().get_session()
        if session:
            try:
                query = """
                UNWIND $memories AS mem
                CREATE (m:Memory {
                    id: mem.id,
                    content: mem.content,
                    source_type: mem.source_type,
                    source_id: mem.source_id,
                    created_at: mem.created_at,
                    updated_at: mem.updated_at,
                    version: 1,
                    is_latest: true,
                    metadata: mem.metadata
                })
                """
                
                memories_data = [
                    {
                        "id": memory_id,
                        "content": chunk,
                        "source_type": "research",
                        "source_id": source_id or "",
                        "created_at": created_at,
                        "updated_at": created_at,
                        "metadata": json.dumps({
                            "title": title,
                            "authors": author_list,
                            "doi": doi,
                            "keywords": keyword_list,
                            "publication_date": publication_date,
                            "type": "research_document",
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "filename": file.filename,
                            "file_type": file_type
                        })
                    }
                    for i, (memory_id, chunk) in enumerate(zip(memory_ids, chunks))
                ]
                
                session.run(query, {"memories": memories_data})
                logger.info(f"Successfully batch added {len(memory_ids)} memories to Neo4j")
            except Exception as e:
                logger.error(f"Failed to batch add memories to Neo4j: {e}")
            finally:
                session.close()
        
        # Create Memory objects for return
        memories = [
            type('Memory', (), {
                'id': memory_id,
                'content': chunk,
                'metadata': {
                    "title": title,
                    "authors": author_list,
                    "doi": doi,
                    "keywords": keyword_list,
                    "publication_date": publication_date,
                    "type": "research_document",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "filename": file.filename,
                    "file_type": file_type
                }
            })()
            for i, (memory_id, chunk) in enumerate(zip(memory_ids, chunks))
        ]
        
        # Skip relationship creation during upload for speed
        
        # Also store in MemMachine
        memmachine_session_id = f"research_{source_id}"
        try:
            full_content = "\n\n".join(chunks)
            await memmachine_service.add_memory(
                session_id=memmachine_session_id,
                messages=[
                    {"role": "system", "content": f"Research Paper: {title}\n\n{full_content}"}
                ],
                metadata={
                    "title": title,
                    "authors": author_list,
                    "doi": doi,
                    "keywords": keyword_list,
                    "publication_date": publication_date,
                    "type": "research_document",
                    "source_id": source_id,
                    "filename": file.filename,
                    "file_type": file_type,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to add research upload to MemMachine: {e}")
        
        return {
            "filename": file.filename,
            "file_type": file_type,
            "title": title,
            "total_chunks": len(chunks),
            "memories_created": len(memories),
            "memory_ids": [m.id for m in memories],
            "source_id": source_id
        }
    except Exception as e:
        logger.error(f"Error uploading research document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/research/search", response_model=dict)
async def search_research(query: str, limit: int = 10):
    """Search research papers with semantic understanding"""
    try:
        results = rag_service.retrieve(
            query=query,
            limit=limit,
            min_similarity=0.6,
            rerank=True
        )
        
        # Filter for research documents only
        research_results = [
            r for r in results
            if r["memory"].metadata.get("type") == "research_document"
        ]
        
        return {
            "query": query,
            "results": [
                {
                    "memory_id": r["memory"].id,
                    "title": r["memory"].metadata.get("title", r["memory"].content[:50]),
                    "authors": r["memory"].metadata.get("authors", []),
                    "abstract": r["memory"].content[:300],
                    "doi": r["memory"].metadata.get("doi"),
                    "similarity": r["final_score"],
                    "keywords": r["memory"].metadata.get("keywords", [])
                }
                for r in research_results
            ],
            "total": len(research_results)
        }
    except Exception as e:
        logger.error(f"Error searching research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export all endpoints
__all__ = ["router"]

