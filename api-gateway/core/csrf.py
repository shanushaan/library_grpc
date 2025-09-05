import secrets
from typing import Optional
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

class CSRFProtection:
    def __init__(self):
        self.tokens = {}
    
    def generate_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def validate_token(self, token: str, session_id: str) -> bool:
        return self.tokens.get(session_id) == token
    
    def store_token(self, token: str, session_id: str):
        self.tokens[session_id] = token
    
    def remove_token(self, session_id: str):
        self.tokens.pop(session_id, None)

csrf_protection = CSRFProtection()

class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exempt_methods=None):
        super().__init__(app)
        self.exempt_methods = exempt_methods or ["GET", "HEAD", "OPTIONS"]
    
    async def dispatch(self, request: Request, call_next):
        if request.method not in self.exempt_methods:
            csrf_token = request.headers.get("X-CSRF-Token")
            session_id = request.headers.get("Authorization", "anonymous")
            
            if not csrf_token or not csrf_protection.validate_token(csrf_token, session_id):
                raise HTTPException(status_code=403, detail={"error": "CSRF token mismatch"})
        
        response = await call_next(request)
        return response