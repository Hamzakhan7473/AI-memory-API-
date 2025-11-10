#!/usr/bin/env python3
"""Check all system services and APIs"""
import asyncio
import sys
import subprocess
import httpx
import redis
from app.core.config import settings
from app.core.database import get_neo4j, get_chroma
from app.services.memmachine_service import memmachine_service

def check_service(name, check_func):
    """Check a service and return status"""
    try:
        result = check_func()
        status = "✅" if result else "❌"
        return f"{status} {name}"
    except Exception as e:
        return f"❌ {name} - Error: {str(e)[:50]}"

def check_http(url):
    """Check HTTP service"""
    try:
        response = httpx.get(url, timeout=5.0)
        return response.status_code == 200
    except:
        return False

def check_docker(container_name):
    """Check Docker container"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return container_name in result.stdout
    except:
        return False

def check_openai():
    """Check OpenAI API"""
    try:
        import openai
        client = openai.OpenAI(api_key=settings.openai_api_key)
        list(client.models.list(limit=1))
        return True
    except:
        return False

def check_cohere():
    """Check Cohere API"""
    try:
        import cohere
        co = cohere.Client(api_key=settings.cohere_api_key)
        return co is not None
    except:
        return False

def check_redis():
    """Check Redis"""
    try:
        if not settings.redis_url:
            return False
        r = redis.from_url(settings.redis_url, decode_responses=True)
        r.ping()
        return True
    except:
        return False

def check_neo4j():
    """Check Neo4j"""
    try:
        session = get_neo4j().get_session()
        if not session:
            return False
        result = session.run("RETURN 1 as test")
        session.close()
        return result is not None
    except:
        return False

def check_chromadb():
    """Check ChromaDB"""
    try:
        chroma = get_chroma()
        chroma.collection.count()
        return True
    except:
        return False

async def check_memmachine():
    """Check MemMachine"""
    try:
        return await memmachine_service.health_check()
    except:
        return False

async def main():
    """Run all checks"""
    print("=" * 60)
    print("SYSTEM STATUS CHECK")
    print("=" * 60)
    print()
    
    # HTTP Services
    print("HTTP Services:")
    print(f"  {check_service('MemMachine (8080)', lambda: check_http('http://localhost:8080/health'))}")
    print(f"  {check_service('FastAPI Backend (8000)', lambda: check_http('http://localhost:8000/health'))}")
    print()
    
    # Docker Services
    print("Docker Containers:")
    print(f"  {check_service('Neo4j', lambda: check_docker('neo4j'))}")
    print(f"  {check_service('PostgreSQL', lambda: check_docker('postgres'))}")
    print()
    
    # APIs
    print("External APIs:")
    print(f"  {check_service('OpenAI API', check_openai)}")
    print(f"  {check_service('Cohere API', check_cohere)}")
    print()
    
    # Databases
    print("Databases:")
    print(f"  {check_service('Redis', check_redis)}")
    print(f"  {check_service('Neo4j Connection', check_neo4j)}")
    print(f"  {check_service('ChromaDB', check_chromadb)}")
    print()
    
    # MemMachine Service
    print("MemMachine Service:")
    memmachine_status = await check_memmachine()
    print(f"  {'✅' if memmachine_status else '❌'} MemMachine Service")
    print()
    
    # Configuration
    print("Configuration:")
    print(f"  {'✅' if settings.openai_api_key else '❌'} OpenAI API Key")
    print(f"  {'✅' if settings.cohere_api_key else '❌'} Cohere API Key")
    print(f"  {'✅' if settings.redis_url else '❌'} Redis URL")
    print()
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
