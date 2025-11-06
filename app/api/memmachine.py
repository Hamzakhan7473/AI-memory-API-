"""
MemMachine proxy router for frontend access
Proxies requests to MemMachine server (port 8080) to avoid CORS issues
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
MEMMACHINE_URL = "http://localhost:8080"

@router.get("/memmachine/health")
async def memmachine_health():
    """Proxy health check to MemMachine"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MEMMACHINE_URL}/health")
            return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        logger.error(f"MemMachine health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"MemMachine unavailable: {str(e)}")

@router.get("/memmachine/v1/sessions")
async def get_sessions():
    """Proxy get sessions request to MemMachine"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MEMMACHINE_URL}/v1/sessions")
            return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        logger.error(f"Get sessions failed: {e}")
        raise HTTPException(status_code=503, detail=f"MemMachine unavailable: {str(e)}")

@router.post("/memmachine/v1/memories")
async def create_memory(request: Request):
    """Proxy create memory request to MemMachine"""
    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MEMMACHINE_URL}/v1/memories",
                json=body,
                timeout=30.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        logger.error(f"Create memory failed: {e}")
        raise HTTPException(status_code=503, detail=f"MemMachine unavailable: {str(e)}")

@router.post("/memmachine/v1/memories/search")
async def search_memories(request: Request):
    """Proxy search memories request to MemMachine"""
    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MEMMACHINE_URL}/v1/memories/search",
                json=body,
                timeout=30.0
            )
            # Handle non-JSON error responses
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = {"detail": response.text or f"MemMachine error: {response.status_code}"}
                return JSONResponse(content=error_data, status_code=response.status_code)
            return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        logger.error(f"Search memories failed: {e}")
        raise HTTPException(status_code=503, detail=f"MemMachine unavailable: {str(e)}")

@router.delete("/memmachine/v1/memories")
async def delete_memories(request: Request):
    """Proxy delete memories request to MemMachine"""
    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{MEMMACHINE_URL}/v1/memories",
                json=body,
                timeout=30.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        logger.error(f"Delete memories failed: {e}")
        raise HTTPException(status_code=503, detail=f"MemMachine unavailable: {str(e)}")

