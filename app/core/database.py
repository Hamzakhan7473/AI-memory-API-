"""
Database connections and setup
"""
from neo4j import GraphDatabase
from chromadb import PersistentClient, Settings as ChromaSettings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Neo4j graph database connection manager"""
    
    def __init__(self):
        self.driver = None
        self.connect()
    
    def connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            # Verify connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            # Fallback to in-memory graph if Neo4j is unavailable
            self.driver = None
    
    def get_session(self):
        """Get a Neo4j session"""
        if self.driver:
            return self.driver.session()
        return None
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()


class ChromaDBConnection:
    """ChromaDB vector database connection manager"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """Establish connection to ChromaDB and create collection"""
        try:
            import os
            os.makedirs(settings.chroma_persist_dir, exist_ok=True)
            self.client = PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )
            # Create or get collection for memories
            self.collection = self.client.get_or_create_collection(
                name="memories",
                metadata={"description": "Memory embeddings with metadata"}
            )
            logger.info("Connected to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise


# Global database connections
neo4j_db = Neo4jConnection()
chroma_db = ChromaDBConnection()


def get_neo4j():
    """Get Neo4j connection"""
    return neo4j_db


def get_chroma():
    """Get ChromaDB connection"""
    return chroma_db

