from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import grpc
import grpc.aio
import sys
import os
import logging
from datetime import datetime
import asyncio

# Add proto generated files to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../grpc-server'))

import library_service_pb2
import library_service_pb2_grpc

# Configure structured JSON logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "service": "api-gateway",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name
        }
        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                    log_entry[key] = value
        return json.dumps(log_entry)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.handlers = [handler]
logger.propagate = False

app = FastAPI(title="Library API Gateway")

# API versioning
API_V1_PREFIX = "/api/v1"

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Async gRPC client connection
async def get_grpc_client():
    grpc_host = os.getenv('GRPC_SERVER_HOST', 'localhost')
    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')
    channel = grpc.aio.insecure_channel(f'{grpc_host}:{grpc_port}')
    return library_service_pb2_grpc.LibraryServiceStub(channel)

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class BookSearchRequest(BaseModel):
    query: str = ""

class IssueBookRequest(BaseModel):
    book_id: int
    user_id: int

class ReturnBookRequest(BaseModel):
    transaction_id: int

class UserBookRequest(BaseModel):
    book_id: int
    request_type: str
    user_id: int
    transaction_id: int = None
    notes: str = None

class RejectBookRequestBody(BaseModel):
    notes: str = ""

# Authentication endpoints
@app.post(f"{API_V1_PREFIX}/login")
async def login(request: LoginRequest):
    logger.info("Login attempt", extra={"username": request.username, "endpoint": "/login"})
    client = await get_grpc_client()
    try:
        response = await client.AuthenticateUser(
            library_service_pb2.AuthRequest(
                username=request.username,
                password=request.password
            )
        )
        
        if response.success:
            logger.info("Login successful", extra={"username": request.username, "role": response.user.role, "user_id": response.user.user_id})
            return {
                "user_id": response.user.user_id,
                "username": response.user.username,
                "email": response.user.email,
                "role": response.user.role,
                "message": response.message
            }
        else:
            logger.warning("Login failed", extra={"username": request.username, "reason": response.message})
            raise HTTPException(status_code=401, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during login", extra={"username": request.username, "error": str(e.details()), "error_type": "grpc_error"})
        raise HTTPException(status_code=500, detail="Service unavailable")
    except Exception as e:
        logger.error("Unexpected error during login", extra={"username": request.username, "error": str(e), "error_type": "unexpected_error"})
        raise HTTPException(status_code=500, detail="Service unavailable")

# Book endpoints
@app.get(f"{API_V1_PREFIX}/user/books/search")
async def search_books(q: str = ""):
    logger.info(f"Book search request with query: '{q}'")
    client = await get_grpc_client()
    try:
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
        
        logger.info(f"Book search completed: {len(books)} books found for query '{q}'")
        return books
    except grpc.RpcError as e:
        logger.error(f"gRPC Error during book search: {e.details()}")
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get(f"{API_V1_PREFIX}/admin/books")
def list_books_admin(q: str = ""):
    logger.info(f"Admin book list request with query: '{q}'")
    return search_books(q)

# Admin book operations
@app.post(f"{API_V1_PREFIX}/admin/issue-book")
def issue_book(request: IssueBookRequest):
    logger.info(f"Admin issuing book: book_id={request.book_id}, user_id={request.user_id}")
    client = get_grpc_client()
    try:
        response = client.IssueBook(
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
def return_book(request: ReturnBookRequest):
    client = get_grpc_client()
    try:
        response = client.ReturnBook(
            library_service_pb2.ReturnBookRequest(
                transaction_id=request.transaction_id,
                admin_id=1  # TODO: Get from auth
            )
        )
        
        if response.success:
            return {
                "transaction_id": response.transaction.transaction_id,
                "fine_amount": response.transaction.fine_amount,
                "message": response.message
            }
        else:
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

# User request endpoints
@app.post(f"{API_V1_PREFIX}/user/book-request")
def create_book_request(request: UserBookRequest):
    logger.info(f"Book request created: user_id={request.user_id}, book_id={request.book_id}, type={request.request_type}")
    client = get_grpc_client()
    try:
        response = client.CreateUserBookRequest(
            library_service_pb2.CreateBookRequestReq(
                user_id=request.user_id,
                book_id=request.book_id,
                request_type=request.request_type,
                transaction_id=request.transaction_id or 0,
                notes=request.notes or ""
            )
        )
        
        if response.success:
            logger.info(f"Book request successful: request_id={response.request.request_id}, status={response.request.status}")
            return {
                "request_id": response.request.request_id,
                "message": response.message,
                "status": response.request.status
            }
        else:
            logger.warning(f"Book request failed: user_id={request.user_id}, book_id={request.book_id} - {response.message}")
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error(f"gRPC Error during book request: user_id={request.user_id}, book_id={request.book_id} - {e.details()}")
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get(f"{API_V1_PREFIX}/admin/book-requests")
async def list_book_requests():
    logger.info("Admin fetching book requests")
    client = await get_grpc_client()
    try:
        # Get all data concurrently
        requests_task = client.GetBookRequests(library_service_pb2.GetBookRequestsReq(status="PENDING"))
        books_task = client.GetBooks(library_service_pb2.GetBooksRequest(search_query=""))
        users_task = client.GetUsers(library_service_pb2.GetUsersRequest())
        
        requests_response, books_response, users_response = await asyncio.gather(
            requests_task, books_task, users_task
        )
        
        # Create lookups
        books_dict = {book.book_id: book for book in books_response.books}
        users_dict = {user.user_id: user.username for user in users_response.users}
        
        requests = []
        for req in requests_response.requests:
            book = books_dict.get(req.book_id)
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
        
        return requests
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get(f"{API_V1_PREFIX}/user/{{user_id}}/book-requests")
def get_user_book_requests(user_id: int):
    logger.info(f"Fetching book requests for user: user_id={user_id}")
    client = get_grpc_client()
    try:
        response = client.GetBookRequests(
            library_service_pb2.GetBookRequestsReq(status="")
        )
        
        # Get books for additional info
        books_response = client.GetBooks(
            library_service_pb2.GetBooksRequest(search_query="")
        )
        books_dict = {book.book_id: book for book in books_response.books}
        
        # Filter requests for specific user
        user_requests = []
        for req in response.requests:
            if req.user_id == user_id:
                book = books_dict.get(req.book_id)
                user_requests.append({
                    "request_id": req.request_id,
                    "user_id": req.user_id,
                    "book_id": req.book_id,
                    "book_title": book.title if book else "Unknown",
                    "book_author": book.author if book else "Unknown",
                    "request_type": req.request_type,
                    "status": req.status,
                    "request_date": req.request_date,
                    "notes": req.notes
                })
        
        return user_requests
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post(f"{API_V1_PREFIX}/admin/book-requests/{{request_id}}/approve")
def approve_book_request(request_id: int):
    logger.info(f"Admin approving book request: request_id={request_id}")
    client = get_grpc_client()
    try:
        response = client.ApproveBookRequest(
            library_service_pb2.ApproveBookRequestReq(
                request_id=request_id,
                admin_id=1  # TODO: Get from auth
            )
        )
        
        if response.success:
            logger.info(f"Book request approved successfully: request_id={request_id}")
            return {"message": response.message}
        else:
            logger.warning(f"Book request approval failed: request_id={request_id} - {response.message}")
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error(f"gRPC Error during book request approval: request_id={request_id} - {e.details()}")
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post(f"{API_V1_PREFIX}/admin/book-requests/{{request_id}}/reject")
def reject_book_request(request_id: int, request_body: RejectBookRequestBody):
    client = get_grpc_client()
    try:
        response = client.RejectBookRequest(
            library_service_pb2.RejectBookRequestReq(
                request_id=request_id,
                admin_id=1,  # TODO: Get from auth
                notes=request_body.notes
            )
        )
        
        if response.success:
            return {"message": response.message}
        else:
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get(f"{API_V1_PREFIX}/admin/users")
def list_users():
    logger.info("Admin fetching users list")
    client = get_grpc_client()
    try:
        response = client.GetUsers(
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
def list_transactions(user_id: int = None, status: str = ""):
    client = get_grpc_client()
    try:
        response = client.GetTransactions(
            library_service_pb2.GetTransactionsRequest(
                user_id=user_id or 0,
                status=status
            )
        )
        
        # Get users and books for additional info
        users_response = client.GetUsers(library_service_pb2.GetUsersRequest())
        books_response = client.GetBooks(library_service_pb2.GetBooksRequest(search_query=""))
        
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
def get_user_stats(user_id: int):
    logger.info(f"Fetching user stats: user_id={user_id}")
    client = get_grpc_client()
    try:
        response = client.GetUserStats(
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
def get_user_transactions(user_id: int, status: str = ""):
    client = get_grpc_client()
    try:
        response = client.GetUserTransactions(
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

@app.get("/")
def root():
    return {"message": "Library API Gateway", "grpc_backend": "localhost:50051"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)