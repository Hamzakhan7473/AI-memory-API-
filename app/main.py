"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import memories, search, graph, dashboard, websocket, memmachine, rag, voice, auth, use_cases
from app.core.config import settings
from app.middleware.performance import PerformanceMiddleware

app = FastAPI(
    title="Enterprise AI Memory Platform",
    description="Enterprise-grade memory management platform with RAG pipeline, voice capabilities, and knowledge graph",
    version="2.0.0"
)

# Performance monitoring middleware
app.add_middleware(PerformanceMiddleware)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(memories.router, prefix="/api/memories", tags=["memories"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])
app.include_router(memmachine.router, prefix="/api", tags=["memmachine"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(use_cases.router, prefix="/api/use-cases", tags=["use-cases"])


@app.get("/")
async def root():
    return {
        "message": "Enterprise AI Memory Platform",
        "version": "2.0.0",
        "features": {
            "rag_pipeline": "✅ Retrieval Augmented Generation with reranking",
            "voice": "✅ Speech-to-text and text-to-speech",
            "authentication": "✅ JWT-based auth with API keys",
            "knowledge_graph": "✅ Neo4j graph database",
            "vector_search": "✅ ChromaDB semantic search",
            "memmachine": "✅ MemMachine integration"
        },
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

