from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from services.auth_service import AuthService
from core.grpc_client import get_grpc_client
from core.validation import validate_username, validate_password
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator('username')
    def validate_username_format(cls, v):
        return validate_username(v)
    
    @validator('password')
    def validate_password_strength(cls, v):
        return validate_password(v)

@router.post('/login')
async def login(request: LoginRequest):
    # Additional business validation
    if not request.username or not request.password:
        logger.warning("Login attempt with empty credentials", extra={"action": "login_empty_credentials"})
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    client = await get_grpc_client()
    auth_service = AuthService(client)
    return await auth_service.authenticate_user(request.username, request.password)