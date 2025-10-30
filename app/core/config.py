"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # ChromaDB Configuration
    chroma_persist_dir: str = "./chroma_db"
    
    # Redis Configuration (optional)
    redis_url: Optional[str] = None
    
    # Application Settings
    api_port: int = 8000
    debug: bool = True
    
    # Embedding Model
    embedding_model: str = "all-MiniLM-L6-v2"  # sentence-transformers default
    use_openai_embeddings: bool = False  # Set to True to use OpenAI embeddings
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

