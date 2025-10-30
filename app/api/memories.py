"""
API endpoints for memory CRUD operations
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from app.core.models import Memory, MemoryCreate, MemoryUpdate, RelationshipType
from app.services.memory_service import memory_service
from app.services.pdf_service import PDFService
from app.api.websocket import notify_memory_created, notify_relationship_created
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=Memory, status_code=201)
async def create_memory(memory_data: MemoryCreate):
    """
    Create a new memory from text input
    """
    try:
        memory = memory_service.create_memory(
            content=memory_data.content,
            metadata=memory_data.metadata,
            source_type=memory_data.source_type,
            source_id=memory_data.source_id
        )
        # Notify WebSocket clients
        await notify_memory_created(memory)
        return memory
    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/from-pdf", response_model=List[Memory], status_code=201)
async def create_memories_from_pdf(
    file: UploadFile = File(...),
    chunk_size: int = Form(default=1000),
    overlap: int = Form(default=200)
):
    """
    Extract text from PDF and create multiple memories from chunks
    """
    try:
        # Read PDF file
        pdf_bytes = await file.read()
        
        # Extract text
        pdf_service = PDFService()
        text = pdf_service.extract_text_from_pdf(pdf_bytes)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from PDF")
        
        # Chunk the text
        chunks = pdf_service.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        
        # Create memories from chunks
        source_id = f"pdf_{file.filename}"
        memories = []
        
        for i, chunk in enumerate(chunks):
            memory = memory_service.create_memory(
                content=chunk,
                metadata={"chunk_index": i, "total_chunks": len(chunks), "filename": file.filename},
                source_type="pdf",
                source_id=source_id
            )
            memories.append(memory)
            
            # Try to find related memories and create EXTEND relationships
            if i > 0:
                # Check similarity with previous chunks
                similar = memory_service.search_similar_memories(
                    chunk,
                    limit=1,
                    min_similarity=0.8
                )
                if similar and similar[0][0] != memory.id:
                    memory_service.create_relationship(
                        similar[0][0],
                        memory.id,
                        RelationshipType.EXTEND,
                        confidence=similar[0][1]
                    )
        
        return memories
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{memory_id}", response_model=Memory)
async def get_memory(memory_id: str):
    """
    Get a memory by ID
    """
    memory = memory_service.get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.get("/", response_model=List[Memory])
async def list_memories(limit: int = 100, offset: int = 0):
    """
    List all memories with pagination
    """
    try:
        memories = memory_service.list_memories(limit=limit, offset=offset)
        return memories
    except Exception as e:
        logger.error(f"Error listing memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{memory_id}", response_model=Memory)
async def update_memory(memory_id: str, memory_data: MemoryUpdate):
    """
    Update an existing memory
    """
    memory = memory_service.update_memory(
        memory_id,
        content=memory_data.content,
        metadata=memory_data.metadata
    )
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(memory_id: str):
    """
    Delete a memory
    """
    success = memory_service.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return None


@router.post("/{memory_id}/relationships", status_code=201)
async def create_relationship(
    memory_id: str,
    target_id: str,
    relationship_type: RelationshipType,
    confidence: float = 0.5
):
    """
    Create a relationship between two memories
    """
    # Verify both memories exist
    source = memory_service.get_memory(memory_id)
    target = memory_service.get_memory(target_id)
    
    if not source:
        raise HTTPException(status_code=404, detail=f"Source memory {memory_id} not found")
    if not target:
        raise HTTPException(status_code=404, detail=f"Target memory {target_id} not found")
    
    relationship = memory_service.create_relationship(
        memory_id,
        target_id,
        relationship_type,
        confidence=confidence
    )
    # Notify WebSocket clients
    await notify_relationship_created(relationship)
    return relationship


@router.get("/{memory_id}/related", response_model=List[Memory])
async def get_related_memories(memory_id: str, relationship_type: Optional[RelationshipType] = None):
    """
    Get memories related to a given memory
    """
    memory = memory_service.get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    related = memory_service.get_related_memories(memory_id, relationship_type)
    return related

