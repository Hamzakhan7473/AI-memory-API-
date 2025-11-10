"""
API endpoints for RAG (Retrieval Augmented Generation) Pipeline
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional, List
from pydantic import BaseModel, Field
from app.services.rag_service import rag_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class RAGQuery(BaseModel):
    """RAG query request model"""
    query: str = Field(..., description="User query")
    retrieval_limit: int = Field(default=10, ge=1, le=50, description="Number of memories to retrieve")
    min_similarity: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum similarity threshold")
    rerank: bool = Field(default=True, description="Whether to use reranking")
    rerank_top_k: Optional[int] = Field(default=None, ge=1, le=50, description="Number of documents to rerank")
    model: str = Field(default="gpt-4", description="LLM model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum tokens in response")
    system_prompt: Optional[str] = Field(default=None, description="Custom system prompt")


class RAGRetrieve(BaseModel):
    """RAG retrieval request model"""
    query: str
    limit: int = Field(default=10, ge=1, le=50)
    min_similarity: float = Field(default=0.5, ge=0.0, le=1.0)
    rerank: bool = True
    rerank_top_k: Optional[int] = Field(default=None, ge=1, le=50)


@router.post("/query", response_model=dict)
async def rag_query(request: RAGQuery):
    """
    Complete RAG pipeline: Retrieve relevant memories and generate response
    
    Example:
    ```json
    {
        "query": "What is machine learning?",
        "retrieval_limit": 10,
        "rerank": true,
        "model": "gpt-4"
    }
    ```
    """
    try:
        result = rag_service.rag_query(
            query=request.query,
            retrieval_limit=request.retrieval_limit,
            min_similarity=request.min_similarity,
            rerank=request.rerank,
            rerank_top_k=request.rerank_top_k,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return result
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrieve", response_model=dict)
async def rag_retrieve(request: RAGRetrieve):
    """
    Retrieve relevant memories with optional reranking (without generation)
    
    Useful for:
    - Testing retrieval quality
    - Building custom generation logic
    - Debugging reranking
    """
    try:
        results = rag_service.retrieve(
            query=request.query,
            limit=request.limit,
            min_similarity=request.min_similarity,
            rerank=request.rerank,
            rerank_top_k=request.rerank_top_k
        )
        
        return {
            "query": request.query,
            "results": [
                {
                    "memory_id": r["memory"].id,
                    "content": r["memory"].content,
                    "similarity_score": r["similarity_score"],
                    "rerank_score": r.get("rerank_score"),
                    "final_score": r["final_score"],
                    "source_type": r["memory"].source_type,
                    "source_id": r["memory"].source_id,
                    "metadata": r["memory"].metadata
                }
                for r in results
            ],
            "total_results": len(results),
            "reranked": request.rerank
        }
    except Exception as e:
        logger.error(f"Error in RAG retrieve: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=dict)
async def rag_generate(request: dict):
    """
    Generate response from provided context (without retrieval)
    
    Request body:
    ```json
    {
        "query": "User question",
        "context": ["Memory 1", "Memory 2", ...],
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    ```
    """
    try:
        query = request.get("query")
        context = request.get("context", [])
        model = request.get("model", "gpt-4")
        temperature = request.get("temperature", 0.7)
        max_tokens = request.get("max_tokens", 1000)
        system_prompt = request.get("system_prompt")
        
        if not query:
            raise HTTPException(status_code=400, detail="query is required")
        
        # Convert context strings to memory-like dicts
        context_memories = [
            {
                "memory": type('obj', (object,), {
                    'id': f"ctx_{i}",
                    'content': ctx,
                    'source_type': "text",
                    'source_id': None
                })(),
                "similarity_score": 1.0,
                "rerank_score": None,
                "final_score": 1.0
            }
            for i, ctx in enumerate(context)
        ]
        
        result = rag_service.generate(
            query=query,
            context_memories=context_memories,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in RAG generate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

