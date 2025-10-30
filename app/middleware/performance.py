"""
Performance monitoring middleware
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log slow requests
        if process_time > 0.4:  # > 400ms
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time*1000:.2f}ms"
            )
        
        # Add timing header
        response.headers["X-Process-Time"] = f"{process_time*1000:.2f}"
        
        return response

