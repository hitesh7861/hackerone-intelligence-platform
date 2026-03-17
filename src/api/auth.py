from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src import config
import hashlib

security = HTTPBearer()

def simple_hash(password: str) -> str:
    """Simple hash for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

DEMO_USERS = {
    "admin": {
        "username": "admin",
        "password": simple_hash("admin123"),
        "role": "admin",
        "organization": None
    },
    "mailru": {
        "username": "mailru",
        "password": simple_hash("mailru123"),
        "role": "customer",
        "organization": "mail_ru"
    },
    "shopify": {
        "username": "shopify",
        "password": simple_hash("shopify123"),
        "role": "customer",
        "organization": "shopify"
    },
    "gitlab": {
        "username": "gitlab",
        "password": simple_hash("gitlab123"),
        "role": "customer",
        "organization": "gitlab"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return simple_hash(plain_password) == hashed_password

def get_password_hash(password: str) -> str:
    return simple_hash(password)

def authenticate_user(username: str, password: str):
    user = DEMO_USERS.get(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.API_SECRET_KEY, algorithm=config.API_ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, config.API_SECRET_KEY, algorithms=[config.API_ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = DEMO_USERS.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
