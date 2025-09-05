from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logging_config import setup_logging
from core.csrf import CSRFMiddleware
from routes.auth import router as auth_router
from routes.books import router as books_router
from routes.requests import router as requests_router
from routes.websocket import router as websocket_router
from routes.users import router as users_router
from routes.transactions import router as transactions_router
from routes.csrf import router as csrf_router

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(title="Library API Gateway")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSRF middleware
app.add_middleware(CSRFMiddleware)

# API versioning
API_V1_PREFIX = "/api/v1"

# Include routers
app.include_router(csrf_router, prefix=API_V1_PREFIX, tags=["CSRF"])
app.include_router(auth_router, prefix=API_V1_PREFIX, tags=["Authentication"])
app.include_router(books_router, prefix=API_V1_PREFIX, tags=["Books"])
app.include_router(requests_router, prefix=API_V1_PREFIX, tags=["Requests"])
app.include_router(websocket_router, tags=["WebSocket"])
app.include_router(users_router, prefix=API_V1_PREFIX, tags=["Users"])
app.include_router(transactions_router, prefix=API_V1_PREFIX, tags=["Transactions"])}

@app.get("/")
async def root():
    return {"message": "Library API Gateway - Modular Version", "grpc_backend": "localhost:50051"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)