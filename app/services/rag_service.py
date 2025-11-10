"""
RAG (Retrieval Augmented Generation) Pipeline Service
Enterprise-grade RAG with reranking and multi-LLM support
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging
import time
import json
from app.core.embeddings import get_embedding
from app.services.memory_service import memory_service
from app.core.database import get_chroma
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """RAG Pipeline with reranking and multi-LLM support"""
    
    def __init__(self):
        self.chroma = get_chroma()
        self.reranker = None
        self._init_reranker()
    
    def _init_reranker(self):
        """Initialize reranking model"""
        try:
            # Try to use Cohere reranker if API key available
            # Otherwise use local BGE reranker
            if hasattr(settings, 'cohere_api_key') and settings.cohere_api_key:
                self.reranker_type = "cohere"
                logger.info("Using Cohere reranker")
            else:
                # Use sentence-transformers reranker
                try:
                    from sentence_transformers import CrossEncoder
                    self.reranker = CrossEncoder('BAAI/bge-reranker-base')
                    self.reranker_type = "bge"
                    logger.info("Using BGE reranker")
                except Exception as e:
                    logger.warning(f"Could not load BGE reranker: {e}")
                    self.reranker_type = "none"
        except Exception as e:
            logger.error(f"Error initializing reranker: {e}")
            self.reranker_type = "none"
    
    def rerank_results(
        self,
        query: str,
        documents: List[str],
        scores: List[float],
        top_k: Optional[int] = None
    ) -> List[Tuple[str, float, int]]:
        """
        Rerank search results using cross-encoder
        
        Args:
            query: Search query
            documents: List of document texts
            scores: Initial similarity scores
            top_k: Number of top results to rerank (None = rerank all)
            
        Returns:
            List of (document, rerank_score, original_index) tuples, sorted by rerank_score
        """
        if not documents or self.reranker_type == "none":
            # Return original results if no reranking available
            results = [(doc, score, idx) for idx, (doc, score) in enumerate(zip(documents, scores))]
            return sorted(results, key=lambda x: x[1], reverse=True)
        
        # Select top K documents for reranking (more efficient)
        if top_k:
            # Sort by initial scores and take top K
            indexed = [(doc, score, idx) for idx, (doc, score) in enumerate(zip(documents, scores))]
            indexed.sort(key=lambda x: x[1], reverse=True)
            top_docs = indexed[:top_k]
            
            rerank_docs = [doc for doc, _, _ in top_docs]
            rerank_indices = [idx for _, _, idx in top_docs]
        else:
            rerank_docs = documents
            rerank_indices = list(range(len(documents)))
        
        try:
            if self.reranker_type == "cohere":
                import cohere
                co = cohere.Client(settings.cohere_api_key)
                
                # Cohere rerank API
                rerank_response = co.rerank(
                    model='rerank-english-v3.0',
                    query=query,
                    documents=rerank_docs,
                    top_n=len(rerank_docs)
                )
                
                # Map reranked results back
                reranked = []
                for result in rerank_response.results:
                    orig_idx = rerank_indices[result.index]
                    reranked.append((
                        documents[orig_idx],
                        result.relevance_score,
                        orig_idx
                    ))
                
                return reranked
                
            elif self.reranker_type == "bge":
                # BGE cross-encoder reranking
                pairs = [[query, doc] for doc in rerank_docs]
                rerank_scores = self.reranker.predict(pairs)
                
                # Combine with original indices
                reranked = [
                    (documents[rerank_indices[i]], float(score), rerank_indices[i])
                    for i, score in enumerate(rerank_scores)
                ]
                
                # Sort by rerank score
                reranked.sort(key=lambda x: x[1], reverse=True)
                return reranked
                
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            # Fallback to original scores
            results = [(doc, scores[idx], idx) for idx in rerank_indices]
            return sorted(results, key=lambda x: x[1], reverse=True)
        
        # Fallback
        results = [(doc, scores[idx], idx) for idx in rerank_indices]
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def retrieve(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.7,
        rerank: bool = True,
        rerank_top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories using semantic search with optional reranking
        
        Args:
            query: Search query
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            rerank: Whether to use reranking
            rerank_top_k: Number of documents to rerank (None = rerank all)
            
        Returns:
            List of dictionaries with memory data and scores
        """
        start_time = time.time()
        
        # Initial retrieval using vector search
        similar_memories = memory_service.search_similar_memories(
            query=query,
            limit=limit * 2 if rerank else limit,  # Get more if reranking
            min_similarity=min_similarity
        )
        
        if not similar_memories:
            return []
        
        # Extract documents and scores
        memory_ids = [mem_id for mem_id, _, _ in similar_memories]
        documents = [content for _, _, content in similar_memories]
        scores = [similarity for _, similarity, _ in similar_memories]
        
        # Rerank if enabled
        if rerank and len(documents) > 1:
            reranked = self.rerank_results(
                query=query,
                documents=documents,
                scores=scores,
                top_k=rerank_top_k or limit * 2
            )
            
            # Take top results after reranking
            reranked = reranked[:limit]
            
            # Build results with reranked scores
            results = []
            for doc, rerank_score, orig_idx in reranked:
                memory_id = memory_ids[orig_idx]
                memory = memory_service.get_memory(memory_id)
                
                if memory:
                    results.append({
                        "memory": memory,
                        "similarity_score": scores[orig_idx],
                        "rerank_score": rerank_score,
                        "final_score": (scores[orig_idx] + rerank_score) / 2,  # Hybrid score
                        "retrieval_time_ms": (time.time() - start_time) * 1000
                    })
        else:
            # No reranking, use original results
            results = []
            for i, (memory_id, similarity, _) in enumerate(similar_memories[:limit]):
                memory = memory_service.get_memory(memory_id)
                if memory:
                    results.append({
                        "memory": memory,
                        "similarity_score": similarity,
                        "rerank_score": None,
                        "final_score": similarity,
                        "retrieval_time_ms": (time.time() - start_time) * 1000
                    })
        
        return results
    
    def generate(
        self,
        query: str,
        context_memories: List[Dict[str, Any]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response using LLM with retrieved context
        
        Args:
            query: User query
            context_memories: Retrieved memories from retrieve()
            model: LLM model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            system_prompt: Optional custom system prompt
            
        Returns:
            Dictionary with generated text, citations, and metadata
        """
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Build context from memories
        context_parts = []
        citations = []
        
        for i, result in enumerate(context_memories, 1):
            memory = result["memory"]
            context_parts.append(f"[{i}] {memory.content}")
            citations.append({
                "memory_id": memory.id,
                "content": memory.content[:200],
                "relevance_score": result["final_score"],
                "source_type": memory.source_type,
                "source_id": memory.source_id
            })
        
        context = "\n\n".join(context_parts)
        
        # Build prompts
        if not system_prompt:
            system_prompt = """You are a helpful AI assistant with access to a knowledge base.
Use the provided context to answer questions accurately. Cite sources using [1], [2], etc.
If the context doesn't contain relevant information, say so."""
        
        user_prompt = f"""Context:
{context}

Question: {query}

Answer based on the context above. Cite sources using [1], [2], etc."""
        
        try:
            # Call OpenAI API
            client = openai.OpenAI(api_key=settings.openai_api_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generated_text = response.choices[0].message.content
            
            return {
                "answer": generated_text,
                "citations": citations,
                "model": model,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def rag_query(
        self,
        query: str,
        retrieval_limit: int = 10,
        min_similarity: float = 0.7,
        rerank: bool = True,
        rerank_top_k: Optional[int] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: Retrieve + Generate
        
        Args:
            query: User query
            retrieval_limit: Number of memories to retrieve
            min_similarity: Minimum similarity threshold
            rerank: Whether to use reranking
            rerank_top_k: Number of documents to rerank
            model: LLM model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Complete RAG response with answer, citations, and metadata
        """
        start_time = time.time()
        
        # Retrieve relevant memories
        retrieved = self.retrieve(
            query=query,
            limit=retrieval_limit,
            min_similarity=min_similarity,
            rerank=rerank,
            rerank_top_k=rerank_top_k
        )
        
        if not retrieved:
            return {
                "answer": "I couldn't find relevant information in the knowledge base.",
                "citations": [],
                "retrieved_memories": [],
                "total_time_ms": (time.time() - start_time) * 1000
            }
        
        # Generate response
        generation_start = time.time()
        generated = self.generate(
            query=query,
            context_memories=retrieved,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "answer": generated["answer"],
            "citations": generated["citations"],
            "retrieved_memories": [
                {
                    "memory_id": r["memory"].id,
                    "content": r["memory"].content[:200],
                    "similarity_score": r["similarity_score"],
                    "rerank_score": r.get("rerank_score"),
                    "final_score": r["final_score"]
                }
                for r in retrieved
            ],
            "model": generated["model"],
            "tokens_used": generated["tokens_used"],
            "retrieval_time_ms": retrieved[0]["retrieval_time_ms"] if retrieved else 0,
            "generation_time_ms": (time.time() - generation_start) * 1000,
            "total_time_ms": (time.time() - start_time) * 1000
        }


# Global service instance
rag_service = RAGService()

