"""
API endpoints for Authentication and Authorization
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.auth_service import (
    auth_service, UserCreate, UserLogin, Token, User
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = auth_service.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


def get_current_user_from_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> User:
    """Dependency to get current user from API key"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    user = auth_service.verify_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user


@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user = auth_service.create_user(user_data)
        # Remove password hash from response
        user.hashed_password = "***"
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token"""
    user = auth_service.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    # Create tokens
    access_token = auth_service.create_access_token(data={"sub": user.id})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60  # 30 minutes
    )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    # Remove password hash
    current_user.hashed_password = "***"
    return current_user


@router.post("/api-keys", response_model=dict)
async def create_api_key(
    name: str = "default",
    current_user: User = Depends(get_current_user)
):
    """Generate a new API key for the current user"""
    api_key = auth_service.generate_api_key(current_user.id, name)
    
    return {
        "api_key": api_key,
        "name": name,
        "message": "Store this API key securely. It will not be shown again."
    }


@router.get("/api-keys", response_model=list)
async def list_api_keys(current_user: User = Depends(get_current_user)):
    """List API keys for current user"""
    keys = [
        {
            "name": key.name,
            "created_at": key.created_at.isoformat(),
            "last_used": key.last_used.isoformat() if key.last_used else None,
            "is_active": key.is_active
        }
        for key in auth_service.api_keys.values()
        if key.user_id == current_user.id
    ]
    
    return keys

