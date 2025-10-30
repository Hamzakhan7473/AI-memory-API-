"""
Embedding generation for semantic understanding
"""
from typing import List, Optional
from app.core.config import settings
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Try to import OpenAI and sentence-transformers
try:
    from openai import OpenAI
    openai_client = None
    if settings.openai_api_key:
        openai_client = OpenAI(api_key=settings.openai_api_key)
except ImportError:
    openai_client = None

try:
    from sentence_transformers import SentenceTransformer
    sentence_model = None
    if not settings.use_openai_embeddings:
        sentence_model = SentenceTransformer(settings.embedding_model)
except ImportError:
    sentence_model = None


def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using configured model
    
    Args:
        text: Input text to embed
        
    Returns:
        List of float values representing the embedding vector
    """
    if settings.use_openai_embeddings and openai_client:
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"OpenAI embedding failed: {e}, falling back to sentence-transformers")
    
    # Fallback to sentence-transformers
    if sentence_model:
        embedding = sentence_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    # Last resort: random embedding (should not happen in production)
    logger.error("No embedding model available, using random embedding")
    return np.random.rand(384).tolist()


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts (batch processing)
    
    Args:
        texts: List of input texts
        
    Returns:
        List of embedding vectors
    """
    if settings.use_openai_embeddings and openai_client:
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.warning(f"OpenAI batch embedding failed: {e}, falling back to sentence-transformers")
    
    # Fallback to sentence-transformers
    if sentence_model:
        embeddings = sentence_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()
    
    # Last resort
    logger.error("No embedding model available, using random embeddings")
    return [np.random.rand(384).tolist() for _ in texts]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score between 0 and 1
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))

