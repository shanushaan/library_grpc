from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import grpc
import grpc.aio
import sys
import os
import logging
from datetime import datetime
import asyncio
import json
from typing import Dict, Optional
import re

# Import services
from services.auth_service import AuthService
from services.book_service import BookService
from services.request_service import RequestService
from services.notification_service import notification_service

# Add proto generated files to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../grpc-server'))

import library_service_pb2
import library_service_pb2_grpc

# Configure structured JSON logging
import json
import traceback

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "service": "api-gateway",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = traceback.format_exception(*record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                    log_entry[key] = value
        return json.dumps(log_entry)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.handlers = [handler]
logger.propagate = False

from fastapi import APIRouter

app = FastAPI(title="Library API Gateway")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API versioning
API_V1_PREFIX = "/api/v1"



# Async gRPC client connection
async def get_grpc_client():
    grpc_host = os.getenv('GRPC_SERVER_HOST', 'localhost')
    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')
    channel = grpc.aio.insecure_channel(f'{grpc_host}:{grpc_port}')
    return library_service_pb2_grpc.LibraryServiceStub(channel)

# Validation functions
def validate_positive_integer(value: int, field_name: str) -> int:
    if value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value

def validate_username(username: str) -> str:
    if not username or len(username.strip()) < 3:
        raise ValueError("Username must be at least 3 characters long")
    if not re.match(r'^[a-zA-Z0-9_]+$', username.strip()):
        raise ValueError("Username can only contain letters, numbers, and underscores")
    return username.strip()

def validate_password(password: str) -> str:
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    return password

def validate_request_type(request_type: str) -> str:
    valid_types = ["ISSUE", "RETURN"]
    if request_type.upper() not in valid_types:
        raise ValueError(f"Request type must be one of: {', '.join(valid_types)}")
    return request_type.upper()

# Pydantic models with validation
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator('username')
    def validate_username_format(cls, v):
        return validate_username(v)
    
    @validator('password')
    def validate_password_strength(cls, v):
        return validate_password(v)

class BookSearchRequest(BaseModel):
    query: str = Field(default="", max_length=200)
    
    @validator('query')
    def validate_query(cls, v):
        return v.strip() if v else ""

class IssueBookRequest(BaseModel):
    book_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    
    @validator('book_id')
    def validate_book_id(cls, v):
        return validate_positive_integer(v, "Book ID")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        return validate_positive_integer(v, "User ID")

class ReturnBookRequest(BaseModel):
    transaction_id: int = Field(..., gt=0)
    
    @validator('transaction_id')
    def validate_transaction_id(cls, v):
        return validate_positive_integer(v, "Transaction ID")

class UserBookRequest(BaseModel):
    book_id: int = Field(..., ge=0)  # Can be 0 for return requests
    request_type: str = Field(..., min_length=1)
    user_id: int = Field(..., gt=0)
    transaction_id: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default="", max_length=500)
    
    @validator('request_type')
    def validate_request_type_format(cls, v):
        return validate_request_type(v)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        return validate_positive_integer(v, "User ID")
    
    @validator('notes')
    def validate_notes(cls, v):
        return v.strip() if v else ""
    
    @validator('transaction_id')
    def validate_transaction_id(cls, v):
        if v is not None and v < 0:
            raise ValueError("Transaction ID must be non-negative")
        return v

class RejectBookRequestBody(BaseModel):
    notes: str = Field(default="", max_length=500)
    
    @validator('notes')
    def validate_notes(cls, v):
        return v.strip() if v else ""

# Authentication endpoints
@app.post(f'{API_V1_PREFIX}/login')
async def login(request: LoginRequest):
    # Additional business validation
    if not request.username or not request.password:
        logger.warning("Login attempt with empty credentials", extra={"action": "login_empty_credentials"})
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    client = await get_grpc_client()
    auth_service = AuthService(client)
    return await auth_service.authenticate_user(request.username, request.password)
    logger.info("Login attempt initiated", extra={"username": request.username, "endpoint": "/login", "action": "auth_start"})
    
    try:
        logger.debug("Establishing gRPC connection for authentication", extra={"username": request.username})
        client = await get_grpc_client()
        
        logger.debug("Sending authentication request to gRPC server", extra={"username": request.username})
        response = await client.AuthenticateUser(
            library_service_pb2.AuthRequest(
                username=request.username,
                password=request.password
            )
        )
        
        if response.success:
            logger.info("Authentication successful", extra={
                "username": request.username, 
                "role": response.user.role, 
                "user_id": response.user.user_id,
                "action": "auth_success"
            })
            return {
                "user_id": response.user.user_id,
                "username": response.user.username,
                "email": response.user.email,
                "role": response.user.role,
                "message": response.message
            }
        else:
            logger.warning("Authentication failed - invalid credentials", extra={
                "username": request.username, 
                "reason": response.message,
                "action": "auth_failed"
            })
            raise HTTPException(status_code=401, detail=response.message)
            
    except grpc.RpcError as e:
        logger.error("gRPC service error during authentication", extra={
            "username": request.username, 
            "grpc_code": e.code().name,
            "grpc_details": str(e.details()),
            "error_type": "grpc_error",
            "action": "auth_grpc_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    except Exception as e:
        logger.error("Unexpected error during authentication", extra={
            "username": request.username, 
            "error": str(e),
            "error_type": "unexpected_error",
            "action": "auth_unexpected_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# Book endpoints
@app.get(f"{API_V1_PREFIX}/user/books/search")
async def search_books(q: str = ""):
    logger.info("Book search initiated", extra={"query": q, "action": "book_search_start"})
    
    try:
        logger.debug("Establishing gRPC connection for book search", extra={"query": q})
        client = await get_grpc_client()
        
        logger.debug("Sending book search request to gRPC server", extra={"query": q})
        response = await client.GetBooks(
            library_service_pb2.GetBooksRequest(search_query=q)
        )
        
        books = []
        for book in response.books:
            books.append({
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "published_year": book.published_year,
                "available_copies": book.available_copies,
                "can_request": book.available_copies > 0
            })
        
        logger.info("Book search completed successfully", extra={
            "query": q, 
            "results_count": len(books),
            "action": "book_search_success"
        })
        return books
        
    except grpc.RpcError as e:
        logger.error("gRPC service error during book search", extra={
            "query": q,
            "grpc_code": e.code().name,
            "grpc_details": str(e.details()),
            "error_type": "grpc_error",
            "action": "book_search_grpc_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Book search service unavailable")
    except Exception as e:
        logger.error("Unexpected error during book search", extra={
            "query": q,
            "error": str(e),
            "error_type": "unexpected_error",
            "action": "book_search_unexpected_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get(f"{API_V1_PREFIX}/admin/books")
async def list_books_admin(q: str = ""):
    logger.info(f"Admin book list request with query: '{q}'")
    return await search_books(q)

# Admin book operations
@app.post(f"{API_V1_PREFIX}/admin/issue-book")
async def issue_book(request: IssueBookRequest):
    # Business rule validation
    logger.debug("Validating book issue request", extra={
        "book_id": request.book_id,
        "user_id": request.user_id
    })
    
    # Validate book exists and is available
    try:
        client = await get_grpc_client()
        books_response = await client.GetBooks(library_service_pb2.GetBooksRequest(search_query=""))
        book = next((b for b in books_response.books if b.book_id == request.book_id), None)
        
        if not book:
            logger.warning("Book issue failed - book not found", extra={
                "book_id": request.book_id,
                "action": "book_issue_book_not_found"
            })
            raise HTTPException(status_code=404, detail="Book not found")
        
        if book.available_copies <= 0:
            logger.warning("Book issue failed - no copies available", extra={
                "book_id": request.book_id,
                "available_copies": book.available_copies,
                "action": "book_issue_no_copies"
            })
            raise HTTPException(status_code=400, detail="No copies available for this book")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error during book validation", extra={
            "book_id": request.book_id,
            "error": str(e)
        }, exc_info=True)
    logger.info(f"Admin issuing book: book_id={request.book_id}, user_id={request.user_id}")
    client = await get_grpc_client()
    try:
        response = await client.IssueBook(
            library_service_pb2.IssueBookRequest(
                book_id=request.book_id,
                member_id=request.user_id,  # Using user_id but proto expects member_id
                admin_id=1  # TODO: Get from auth
            )
        )
        
        if response.success:
            logger.info(f"Book issued successfully: transaction_id={response.transaction.transaction_id}")
            return {
                "transaction_id": response.transaction.transaction_id,
                "message": response.message
            }
        else:
            logger.warning(f"Book issue failed: book_id={request.book_id}, user_id={request.user_id} - {response.message}")
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error(f"gRPC Error during book issue: book_id={request.book_id}, user_id={request.user_id} - {e.details()}")
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post(f"{API_V1_PREFIX}/admin/return-book")
async def return_book(request: ReturnBookRequest):
    logger.info("Book return initiated", extra={
        "transaction_id": request.transaction_id,
        "action": "book_return_start"
    })
    
    try:
        logger.debug("Establishing gRPC connection for book return", extra={"transaction_id": request.transaction_id})
        client = await get_grpc_client()
        
        logger.debug("Sending book return request to gRPC server", extra={"transaction_id": request.transaction_id})
        response = await client.ReturnBook(
            library_service_pb2.ReturnBookRequest(
                transaction_id=request.transaction_id,
                admin_id=1  # TODO: Get from auth
            )
        )
        
        if response.success:
            logger.info("Book returned successfully", extra={
                "transaction_id": response.transaction.transaction_id,
                "fine_amount": response.transaction.fine_amount,
                "action": "book_return_success"
            })
            return {
                "transaction_id": response.transaction.transaction_id,
                "fine_amount": response.transaction.fine_amount,
                "message": response.message
            }
        else:
            logger.warning("Book return failed", extra={
                "transaction_id": request.transaction_id,
                "reason": response.message,
                "action": "book_return_failed"
            })
            raise HTTPException(status_code=400, detail=response.message)
            
    except grpc.RpcError as e:
        logger.error("gRPC service error during book return", extra={
            "transaction_id": request.transaction_id,
            "grpc_code": e.code().name,
            "grpc_details": str(e.details()),
            "error_type": "grpc_error",
            "action": "book_return_grpc_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Book return service unavailable")
    except Exception as e:
        logger.error("Unexpected error during book return", extra={
            "transaction_id": request.transaction_id,
            "error": str(e),
            "error_type": "unexpected_error",
            "action": "book_return_unexpected_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# User request endpoints
@app.post(f"{API_V1_PREFIX}/user/book-request")
async def create_book_request(request: UserBookRequest):
    # Business rule validation
    logger.debug("Validating user book request", extra={
        "user_id": request.user_id,
        "book_id": request.book_id,
        "request_type": request.request_type
    })
    
    # Validate request type specific rules
    if request.request_type == "ISSUE":
        if request.book_id <= 0:
            logger.warning("Issue request with invalid book_id", extra={
                "user_id": request.user_id,
                "book_id": request.book_id,
                "action": "book_request_invalid_book_id"
            })
            raise HTTPException(status_code=400, detail="Valid book ID required for issue requests")
    
    elif request.request_type == "RETURN":
        if not request.transaction_id or request.transaction_id <= 0:
            logger.warning("Return request without valid transaction_id", extra={
                "user_id": request.user_id,
                "transaction_id": request.transaction_id,
                "action": "book_request_invalid_transaction_id"
            })
            raise HTTPException(status_code=400, detail="Valid transaction ID required for return requests")
    logger.info("User book request initiated", extra={
        "user_id": request.user_id,
        "book_id": request.book_id,
        "request_type": request.request_type,
        "transaction_id": request.transaction_id,
        "action": "user_book_request_start"
    })
    
    try:
        logger.debug("Establishing gRPC connection for book request", extra={
            "user_id": request.user_id,
            "book_id": request.book_id,
            "request_type": request.request_type
        })
        client = await get_grpc_client()
        
        logger.debug("Sending book request to gRPC server", extra={
            "user_id": request.user_id,
            "book_id": request.book_id,
            "request_type": request.request_type
        })
        response = await client.CreateUserBookRequest(
            library_service_pb2.CreateBookRequestReq(
                user_id=request.user_id,
                book_id=request.book_id,
                request_type=request.request_type,
                transaction_id=request.transaction_id or 0,
                notes=request.notes or ""
            )
        )
        
        if response.success:
            logger.info("User book request created successfully", extra={
                "user_id": request.user_id,
                "book_id": request.book_id,
                "request_type": request.request_type,
                "request_id": response.request.request_id,
                "status": response.request.status,
                "action": "user_book_request_success"
            })
            return {
                "request_id": response.request.request_id,
                "message": response.message,
                "status": response.request.status
            }
        else:
            logger.warning("User book request failed", extra={
                "user_id": request.user_id,
                "book_id": request.book_id,
                "request_type": request.request_type,
                "reason": response.message,
                "action": "user_book_request_failed"
            })
            raise HTTPException(status_code=400, detail=response.message)
            
    except grpc.RpcError as e:
        logger.error("gRPC service error during book request", extra={
            "user_id": request.user_id,
            "book_id": request.book_id,
            "request_type": request.request_type,
            "grpc_code": e.code().name,
            "grpc_details": str(e.details()),
            "error_type": "grpc_error",
            "action": "user_book_request_grpc_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Book request service unavailable")
    except Exception as e:
        logger.error("Unexpected error during book request", extra={
            "user_id": request.user_id,
            "book_id": request.book_id,
            "request_type": request.request_type,
            "error": str(e),
            "error_type": "unexpected_error",
            "action": "user_book_request_unexpected_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get(f"{API_V1_PREFIX}/admin/book-requests")
async def list_book_requests():
    logger.info("Admin book requests list initiated", extra={"action": "admin_book_requests_start"})
    
    try:
        logger.debug("Establishing gRPC connection for admin book requests")
        client = await get_grpc_client()
        
        logger.debug("Fetching concurrent data: requests, books, users")
        # Get all data concurrently
        requests_task = client.GetBookRequests(library_service_pb2.GetBookRequestsReq(status="PENDING"))
        books_task = client.GetBooks(library_service_pb2.GetBooksRequest(search_query=""))
        users_task = client.GetUsers(library_service_pb2.GetUsersRequest())
        
        requests_response, books_response, users_response = await asyncio.gather(
            requests_task, books_task, users_task
        )
        
        logger.debug("Processing fetched data", extra={
            "requests_count": len(requests_response.requests),
            "books_count": len(books_response.books),
            "users_count": len(users_response.users)
        })
        
        # Create lookups
        books_dict = {book.book_id: book for book in books_response.books}
        users_dict = {user.user_id: user.username for user in users_response.users}
        
        requests = []
        for req in requests_response.requests:
            book = books_dict.get(req.book_id)
            if not book and req.book_id > 0:
                logger.warning("Book not found for request", extra={
                    "request_id": req.request_id,
                    "book_id": req.book_id
                })
            
            requests.append({
                "request_id": req.request_id,
                "user_id": req.user_id,
                "user_name": users_dict.get(req.user_id, f"User {req.user_id}"),
                "book_id": req.book_id,
                "book_title": book.title if book else "Unknown",
                "book_author": book.author if book else "Unknown",
                "available_copies": book.available_copies if book else 0,
                "request_type": req.request_type,
                "status": req.status,
                "request_date": req.request_date,
                "notes": req.notes
            })
        
        logger.info("Admin book requests retrieved successfully", extra={
            "total_requests": len(requests),
            "action": "admin_book_requests_success"
        })
        return requests
        
    except grpc.RpcError as e:
        logger.error("gRPC service error during admin book requests fetch", extra={
            "grpc_code": e.code().name,
            "grpc_details": str(e.details()),
            "error_type": "grpc_error",
            "action": "admin_book_requests_grpc_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Book requests service unavailable")
    except Exception as e:
        logger.error("Unexpected error during admin book requests fetch", extra={
            "error": str(e),
            "error_type": "unexpected_error",
            "action": "admin_book_requests_unexpected_error"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get(f"{API_V1_PREFIX}/user/{{user_id}}/book-requests")
async def get_user_book_requests(user_id: int):
    # Input validation
    if user_id <= 0:
        logger.warning("Invalid user_id for book requests", extra={
            "user_id": user_id,
            "action": "get_user_requests_invalid_user_id"
        })
        raise HTTPException(status_code=400, detail="Valid user ID required")
    logger.info(f"Fetching book requests for user: user_id={user_id}")
    client = await get_grpc_client()
    try:
        response = await client.GetBookRequests(
            library_service_pb2.GetBookRequestsReq(status="")
        )
        
        # Get books and transactions for additional info
        books_response = await client.GetBooks(
            library_service_pb2.GetBooksRequest(search_query="")
        )
        transactions_response = await client.GetTransactions(
            library_service_pb2.GetTransactionsRequest(user_id=user_id, status="")
        )
        
        books_dict = {book.book_id: book for book in books_response.books}
        transactions_dict = {txn.transaction_id: txn for txn in transactions_response.transactions}
        
        # Filter requests for specific user
        user_requests = []
        for req in response.requests:
            if req.user_id == user_id:
                book_title = "Unknown"
                book_author = "Unknown"
                
                if req.request_type == "RETURN" and req.transaction_id and req.transaction_id > 0:
                    # Use transaction_id to get book details for return requests
                    transaction = transactions_dict.get(req.transaction_id)
                    if transaction:
                        book = books_dict.get(transaction.book_id)
                        if book:
                            book_title = book.title
                            book_author = book.author
                elif req.book_id > 0:
                    # Use book_id for issue requests
                    book = books_dict.get(req.book_id)
                    if book:
                        book_title = book.title
                        book_author = book.author
                
                user_requests.append({
                    "request_id": req.request_id,
                    "user_id": req.user_id,
                    "book_id": req.book_id,
                    "book_title": book_title,
                    "book_author": book_author,
                    "request_type": req.request_type,
                    "status": req.status,
                    "request_date": req.request_date,
                    "notes": req.notes
                })
        
        return user_requests
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post(f"{API_V1_PREFIX}/admin/book-requests/{{request_id}}/approve")
async def approve_book_request(request_id: int):
    # Input validation
    if request_id <= 0:
        logger.warning("Invalid request_id for approval", extra={
            "request_id": request_id,
            "action": "approve_invalid_request_id"
        })
        raise HTTPException(status_code=400, detail="Valid request ID required")
    logger.info(f"Admin approving book request: request_id={request_id}")
    client = await get_grpc_client()
    try:
        response = await client.ApproveBookRequest(
            library_service_pb2.ApproveBookRequestReq(
                request_id=request_id,
                admin_id=1  # TODO: Get from auth
            )
        )
        
        if response.success:
            logger.info("Book request approved successfully", extra={
                "request_id": request_id,
                "action": "request_approved"
            })
            
            try:
                # Get request details for notification
                logger.debug("Fetching request details for notification", extra={"request_id": request_id})
                requests_response = await client.GetBookRequests(library_service_pb2.GetBookRequestsReq(status=""))
                approved_request = next((req for req in requests_response.requests if req.request_id == request_id), None)
                
                if approved_request:
                    logger.debug("Sending approval notification", extra={
                        "request_id": request_id,
                        "user_id": approved_request.user_id,
                        "request_type": approved_request.request_type
                    })
                    await send_notification(approved_request.user_id, {
                        "type": "REQUEST_APPROVED",
                        "message": f"Your {approved_request.request_type.lower()} request has been approved",
                        "requestId": request_id
                    })
                else:
                    logger.warning("Approved request not found for notification", extra={"request_id": request_id})
                    
            except Exception as e:
                logger.error("Failed to send approval notification", extra={
                    "request_id": request_id,
                    "error": str(e)
                }, exc_info=True)
            
            return {"message": response.message}
        else:
            logger.warning(f"Book request approval failed: request_id={request_id} - {response.message}")
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error(f"gRPC Error during book request approval: request_id={request_id} - {e.details()}")
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post(f"{API_V1_PREFIX}/admin/book-requests/{{request_id}}/reject")
async def reject_book_request(request_id: int, request_body: RejectBookRequestBody):
    # Input validation
    if request_id <= 0:
        logger.warning("Invalid request_id for rejection", extra={
            "request_id": request_id,
            "action": "reject_invalid_request_id"
        })
        raise HTTPException(status_code=400, detail="Valid request ID required")
    client = await get_grpc_client()
    try:
        response = await client.RejectBookRequest(
            library_service_pb2.RejectBookRequestReq(
                request_id=request_id,
                admin_id=1,  # TODO: Get from auth
                notes=request_body.notes
            )
        )
        
        if response.success:
            logger.info("Book request rejected successfully", extra={
                "request_id": request_id,
                "action": "request_rejected"
            })
            
            try:
                # Get request details for notification
                logger.debug("Fetching request details for rejection notification", extra={"request_id": request_id})
                requests_response = await client.GetBookRequests(library_service_pb2.GetBookRequestsReq(status=""))
                rejected_request = next((req for req in requests_response.requests if req.request_id == request_id), None)
                
                if rejected_request:
                    logger.debug("Sending rejection notification", extra={
                        "request_id": request_id,
                        "user_id": rejected_request.user_id,
                        "request_type": rejected_request.request_type
                    })
                    await send_notification(rejected_request.user_id, {
                        "type": "REQUEST_REJECTED",
                        "message": f"Your {rejected_request.request_type.lower()} request has been rejected",
                        "requestId": request_id
                    })
                else:
                    logger.warning("Rejected request not found for notification", extra={"request_id": request_id})
                    
            except Exception as e:
                logger.error("Failed to send rejection notification", extra={
                    "request_id": request_id,
                    "error": str(e)
                }, exc_info=True)
            
            return {"message": response.message}
        else:
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get(f"{API_V1_PREFIX}/admin/users")
async def list_users():
    logger.info("Admin fetching users list")
    client = await get_grpc_client()
    try:
        response = await client.GetUsers(
            library_service_pb2.GetUsersRequest()
        )
        
        users = []
        for user in response.users:
            users.append({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active
            })
        
        return users
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get(f"{API_V1_PREFIX}/admin/transactions")
async def list_transactions(user_id: int = None, status: str = ""):
    # Input validation
    if user_id is not None and user_id < 0:
        logger.warning("Invalid user_id for admin transactions", extra={
            "user_id": user_id,
            "action": "admin_transactions_invalid_user_id"
        })
        raise HTTPException(status_code=400, detail="User ID must be non-negative")
    
    # Validate status if provided
    if status and status.strip():
        valid_statuses = ["BORROWED", "RETURNED", "OVERDUE"]
        if status.upper() not in valid_statuses:
            logger.warning("Invalid status for admin transactions", extra={
                "user_id": user_id,
                "status": status,
                "action": "admin_transactions_invalid_status"
            })
            raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(valid_statuses)}")
    client = await get_grpc_client()
    try:
        response = await client.GetTransactions(
            library_service_pb2.GetTransactionsRequest(
                user_id=user_id or 0,
                status=status
            )
        )
        
        # Get users and books for additional info
        users_response = await client.GetUsers(library_service_pb2.GetUsersRequest())
        books_response = await client.GetBooks(library_service_pb2.GetBooksRequest(search_query=""))
        
        users_dict = {user.user_id: user.username for user in users_response.users}
        books_dict = {book.book_id: book.title for book in books_response.books}
        
        transactions = []
        for txn in response.transactions:
            transactions.append({
                "transaction_id": txn.transaction_id,
                "user_id": txn.member_id,
                "username": users_dict.get(txn.member_id, f"User {txn.member_id}"),
                "book_id": txn.book_id,
                "book_title": books_dict.get(txn.book_id, "Unknown Book"),
                "transaction_type": txn.transaction_type,
                "transaction_date": txn.transaction_date,
                "due_date": txn.due_date,
                "return_date": txn.return_date,
                "status": txn.status,
                "fine_amount": txn.fine_amount
            })
        
        return transactions
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get(f"{API_V1_PREFIX}/user/{{user_id}}/stats")
async def get_user_stats(user_id: int):
    # Input validation
    if user_id <= 0:
        logger.warning("Invalid user_id for stats", extra={
            "user_id": user_id,
            "action": "get_user_stats_invalid_user_id"
        })
        raise HTTPException(status_code=400, detail="Valid user ID required")
    logger.info(f"Fetching user stats: user_id={user_id}")
    client = await get_grpc_client()
    try:
        response = await client.GetUserStats(
            library_service_pb2.UserStatsRequest(user_id=user_id)
        )
        
        stats = {
            "total_books_taken": response.total_books_taken,
            "currently_borrowed": response.currently_borrowed,
            "overdue_books": response.overdue_books,
            "total_fine": response.total_fine
        }
        logger.info(f"User stats retrieved: user_id={user_id}, borrowed={stats['currently_borrowed']}, overdue={stats['overdue_books']}")
        return stats
    except grpc.RpcError as e:
        logger.error(f"gRPC Error fetching user stats: user_id={user_id} - {e.details()}")
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get(f"{API_V1_PREFIX}/user/{{user_id}}/transactions")
async def get_user_transactions(user_id: int, status: str = ""):
    # Input validation
    if user_id <= 0:
        logger.warning("Invalid user_id for transactions", extra={
            "user_id": user_id,
            "action": "get_user_transactions_invalid_user_id"
        })
        raise HTTPException(status_code=400, detail="Valid user ID required")
    
    # Validate status if provided
    if status and status.strip():
        valid_statuses = ["BORROWED", "RETURNED", "OVERDUE"]
        if status.upper() not in valid_statuses:
            logger.warning("Invalid status for transactions", extra={
                "user_id": user_id,
                "status": status,
                "action": "get_user_transactions_invalid_status"
            })
            raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(valid_statuses)}")
    client = await get_grpc_client()
    try:
        response = await client.GetUserTransactions(
            library_service_pb2.GetUserTransactionsRequest(
                user_id=user_id,
                status=status
            )
        )
        
        transactions = []
        for txn in response.transactions:
            transactions.append({
                "transaction_id": txn.transaction_id,
                "book_id": txn.book_id,
                "book_title": txn.book_title,
                "book_author": txn.book_author,
                "transaction_type": txn.transaction_type,
                "transaction_date": txn.transaction_date,
                "due_date": txn.due_date,
                "return_date": txn.return_date,
                "status": txn.status,
                "fine_amount": txn.fine_amount
            })
        
        return transactions
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    # Validate WebSocket connection parameters
    query_params = dict(websocket.query_params)
    user_id = query_params.get('userId')
    
    if user_id and not user_id.isdigit():
        logger.warning("WebSocket connection with invalid userId format", extra={
            "user_id": user_id,
            "action": "ws_invalid_user_id_format"
        })
        await websocket.close(code=4000, reason="Invalid userId format")
        return
    user_id = None
    try:
        logger.debug("WebSocket connection attempt", extra={"action": "ws_connect_start"})
        await websocket.accept()
        
        # Get userId from query parameters
        query_params = dict(websocket.query_params)
        user_id = query_params.get('userId')
        
        if user_id:
            user_connections[user_id] = websocket
            logger.info("WebSocket connection established", extra={
                "user_id": user_id,
                "action": "ws_connected",
                "total_connections": len(user_connections)
            })
        else:
            logger.warning("WebSocket connection without user_id", extra={"action": "ws_no_user_id"})
        
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        if user_id and user_id in user_connections:
            del user_connections[user_id]
            logger.info("WebSocket connection closed", extra={
                "user_id": user_id,
                "action": "ws_disconnected",
                "total_connections": len(user_connections)
            })
    except Exception as e:
        logger.error("WebSocket connection error", extra={
            "user_id": user_id,
            "error": str(e),
            "action": "ws_error"
        }, exc_info=True)
        if user_id and user_id in user_connections:
            del user_connections[user_id]

async def send_notification(user_id: int, notification: dict):
    user_id_str = str(user_id)
    logger.debug("Attempting to send notification", extra={
        "user_id": user_id,
        "notification_type": notification.get('type'),
        "action": "notification_send_start"
    })
    
    if user_id_str in user_connections:
        try:
            await user_connections[user_id_str].send_text(json.dumps(notification))
            logger.info("Notification sent successfully", extra={
                "user_id": user_id,
                "notification_type": notification.get('type'),
                "action": "notification_sent"
            })
        except Exception as e:
            logger.warning("Failed to send notification - removing dead connection", extra={
                "user_id": user_id,
                "error": str(e),
                "action": "notification_failed"
            })
            if user_id_str in user_connections:
                del user_connections[user_id_str]
    else:
        logger.debug("User not connected - notification not sent", extra={
            "user_id": user_id,
            "notification_type": notification.get('type'),
            "action": "notification_no_connection"
        })

@app.get("/")
async def root():
    return {"message": "Library API Gateway - Async Version", "grpc_backend": "localhost:50051"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)