"""
Enterprise Authentication and Authorization Service
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import secrets
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Generate random secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = datetime.utcnow()


class UserCreate(BaseModel):
    """User creation request"""
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class APIKey(BaseModel):
    """API Key model"""
    key: str
    user_id: str
    name: str
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True


class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}  # In-memory for now, replace with DB
        self.api_keys: Dict[str, APIKey] = {}
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        # bcrypt has a 72 byte limit, truncate if necessary
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        import uuid
        
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        # Check if email already exists
        for existing_user in self.users.values():
            if existing_user.email == user_data.email:
                raise ValueError("Email already registered")
        
        user = User(
            id=user_id,
            email=user_data.email,
            username=user_data.username,
            hashed_password=self.hash_password(user_data.password)
        )
        
        self.users[user_id] = user
        logger.info(f"Created user: {user_id}")
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user and return User object"""
        for user in self.users.values():
            if user.email == email:
                if self.verify_password(password, user.hashed_password):
                    return user
                break
        return None
    
    def generate_api_key(self, user_id: str, name: str = "default") -> str:
        """Generate API key for user"""
        api_key = f"ak_{secrets.token_urlsafe(32)}"
        
        key_obj = APIKey(
            key=api_key,
            user_id=user_id,
            name=name,
            created_at=datetime.utcnow()
        )
        
        self.api_keys[api_key] = key_obj
        logger.info(f"Generated API key for user: {user_id}")
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[User]:
        """Verify API key and return user"""
        key_obj = self.api_keys.get(api_key)
        if not key_obj or not key_obj.is_active:
            return None
        
        # Update last used
        key_obj.last_used = datetime.utcnow()
        
        return self.users.get(key_obj.user_id)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)


# Global service instance
auth_service = AuthService()

