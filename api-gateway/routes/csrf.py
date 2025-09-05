from fastapi import APIRouter, Request
from core.csrf import csrf_protection

router = APIRouter()

@router.get("/csrf-token")
async def get_csrf_token(request: Request):
    session_id = request.headers.get("Authorization", "anonymous")
    token = csrf_protection.generate_token()
    csrf_protection.store_token(token, session_id)
    return {"token": token}