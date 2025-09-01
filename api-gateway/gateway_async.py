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

class CreateBookRequest(BaseModel):
    title: str
    author: str
    genre: str
    published_year: int
    available_copies: int

class UpdateBookRequest(BaseModel):
    book_id: int
    title: str
    author: str
    genre: str
    published_year: int
    available_copies: int

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

class UpdateUserRequest(BaseModel):
    username: str
    email: str
    role: str
    is_active: bool
    password: str = None

# Convert all endpoints to async
@app.post("/login")
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

@app.get("/user/books/search")
async def search_books(q: str = ""):
    logger.info("Book search request", extra={"query": q})
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
        
        logger.info("Book search completed", extra={"query": q, "results_count": len(books)})
        return books
    except grpc.RpcError as e:
        logger.error("gRPC Error during book search", extra={"query": q, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post("/user/book-request")
async def create_book_request(request: UserBookRequest):
    logger.info("Book request created", extra={"user_id": request.user_id, "book_id": request.book_id, "request_type": request.request_type})
    client = await get_grpc_client()
    try:
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
            logger.info("Book request successful", extra={"request_id": response.request.request_id, "status": response.request.status})
            return {
                "request_id": response.request.request_id,
                "message": response.message,
                "status": response.request.status
            }
        else:
            logger.warning("Book request failed", extra={"user_id": request.user_id, "book_id": request.book_id, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during book request", extra={"user_id": request.user_id, "book_id": request.book_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get("/admin/book-requests")
async def list_book_requests():
    logger.info("Admin fetching book requests")
    client = await get_grpc_client()
    try:
        # Concurrent API calls for better performance
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
        
        logger.info("Admin book requests retrieved", extra={"requests_count": len(requests)})
        return requests
    except grpc.RpcError as e:
        logger.error("gRPC Error fetching admin book requests", extra={"error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get("/user/{user_id}/stats")
async def get_user_stats(user_id: int):
    logger.info("Fetching user stats", extra={"user_id": user_id})
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
        logger.info("User stats retrieved", extra={"user_id": user_id, "borrowed": stats['currently_borrowed'], "overdue": stats['overdue_books']})
        return stats
    except grpc.RpcError as e:
        logger.error("gRPC Error fetching user stats", extra={"user_id": user_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get("/user/{user_id}/transactions")
async def get_user_transactions(user_id: int, status: str = ""):
    logger.info("Fetching user transactions", extra={"user_id": user_id, "status": status})
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
        
        logger.info("User transactions retrieved", extra={"user_id": user_id, "transactions_count": len(transactions)})
        return transactions
    except grpc.RpcError as e:
        logger.error("gRPC Error fetching user transactions", extra={"user_id": user_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get("/admin/books")
async def list_books_admin(q: str = ""):
    logger.info("Admin book list request", extra={"query": q})
    return await search_books(q)

@app.post("/admin/issue-book")
async def issue_book(request: IssueBookRequest):
    logger.info("Admin issuing book", extra={"book_id": request.book_id, "user_id": request.user_id})
    client = await get_grpc_client()
    try:
        response = await client.IssueBook(
            library_service_pb2.IssueBookRequest(
                book_id=request.book_id,
                member_id=request.user_id,
                admin_id=1
            )
        )
        
        if response.success:
            logger.info("Book issued successfully", extra={"transaction_id": response.transaction.transaction_id})
            return {
                "transaction_id": response.transaction.transaction_id,
                "message": response.message
            }
        else:
            logger.warning("Book issue failed", extra={"book_id": request.book_id, "user_id": request.user_id, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during book issue", extra={"book_id": request.book_id, "user_id": request.user_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post("/admin/return-book")
async def return_book(request: ReturnBookRequest):
    logger.info("Admin returning book", extra={"transaction_id": request.transaction_id})
    client = await get_grpc_client()
    try:
        response = await client.ReturnBook(
            library_service_pb2.ReturnBookRequest(
                transaction_id=request.transaction_id,
                admin_id=1
            )
        )
        
        if response.success:
            logger.info("Book returned successfully", extra={"transaction_id": response.transaction.transaction_id, "fine": response.transaction.fine_amount})
            return {
                "transaction_id": response.transaction.transaction_id,
                "fine_amount": response.transaction.fine_amount,
                "message": response.message
            }
        else:
            logger.warning("Book return failed", extra={"transaction_id": request.transaction_id, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during book return", extra={"transaction_id": request.transaction_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get("/user/{user_id}/book-requests")
async def get_user_book_requests(user_id: int):
    logger.info("Fetching user book requests", extra={"user_id": user_id})
    client = await get_grpc_client()
    try:
        requests_task = client.GetBookRequests(library_service_pb2.GetBookRequestsReq(status=""))
        books_task = client.GetBooks(library_service_pb2.GetBooksRequest(search_query=""))
        
        requests_response, books_response = await asyncio.gather(requests_task, books_task)
        
        books_dict = {book.book_id: book for book in books_response.books}
        
        user_requests = []
        for req in requests_response.requests:
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
        
        logger.info("User book requests retrieved", extra={"user_id": user_id, "requests_count": len(user_requests)})
        return user_requests
    except grpc.RpcError as e:
        logger.error("gRPC Error fetching user book requests", extra={"user_id": user_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post("/admin/book-requests/{request_id}/approve")
async def approve_book_request(request_id: int):
    logger.info("Admin approving book request", extra={"request_id": request_id})
    client = await get_grpc_client()
    try:
        response = await client.ApproveBookRequest(
            library_service_pb2.ApproveBookRequestReq(
                request_id=request_id,
                admin_id=1
            )
        )
        
        if response.success:
            logger.info("Book request approved successfully", extra={"request_id": request_id})
            return {"message": response.message}
        else:
            logger.warning("Book request approval failed", extra={"request_id": request_id, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during book request approval", extra={"request_id": request_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post("/admin/book-requests/{request_id}/reject")
async def reject_book_request(request_id: int, notes: str = ""):
    logger.info("Admin rejecting book request", extra={"request_id": request_id})
    client = await get_grpc_client()
    try:
        response = await client.RejectBookRequest(
            library_service_pb2.RejectBookRequestReq(
                request_id=request_id,
                admin_id=1,
                notes=notes
            )
        )
        
        if response.success:
            logger.info("Book request rejected successfully", extra={"request_id": request_id})
            return {"message": response.message}
        else:
            logger.warning("Book request rejection failed", extra={"request_id": request_id, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during book request rejection", extra={"request_id": request_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get("/admin/users")
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
        
        logger.info("Admin users list retrieved", extra={"users_count": len(users)})
        return users
    except grpc.RpcError as e:
        logger.error("gRPC Error fetching users list", extra={"error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get("/admin/transactions")
async def list_transactions(user_id: int = None, status: str = "", page: int = 1, limit: int = 20):
    logger.info("Admin fetching transactions", extra={"user_id": user_id, "status": status, "page": page, "limit": limit})
    client = await get_grpc_client()
    try:
        transactions_task = client.GetTransactions(
            library_service_pb2.GetTransactionsRequest(
                user_id=user_id or 0,
                status=status
            )
        )
        users_task = client.GetUsers(library_service_pb2.GetUsersRequest())
        books_task = client.GetBooks(library_service_pb2.GetBooksRequest(search_query=""))
        
        transactions_response, users_response, books_response = await asyncio.gather(
            transactions_task, users_task, books_task
        )
        
        users_dict = {user.user_id: user.username for user in users_response.users}
        books_dict = {book.book_id: book.title for book in books_response.books}
        
        all_transactions = []
        for txn in transactions_response.transactions:
            all_transactions.append({
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
        
        # Pagination
        total_count = len(all_transactions)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        transactions = all_transactions[start_idx:end_idx]
        
        logger.info("Admin transactions retrieved", extra={"total_count": total_count, "page": page, "returned_count": len(transactions)})
        return {
            "transactions": transactions,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
    except grpc.RpcError as e:
        logger.error("gRPC Error fetching transactions", extra={"error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get("/admin/stats")
async def get_admin_stats():
    client = await get_grpc_client()
    try:
        transactions_response = await client.GetTransactions(
            library_service_pb2.GetTransactionsRequest(user_id=0, status="")
        )
        
        borrowed_count = sum(1 for txn in transactions_response.transactions if txn.status == 'BORROWED')
        overdue_count = sum(1 for txn in transactions_response.transactions 
                           if txn.status == 'BORROWED' and txn.due_date < datetime.now().isoformat())
        
        return {
            "borrowed_books": borrowed_count,
            "overdue_books": overdue_count
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post("/admin/books")
async def create_book(request: CreateBookRequest):
    logger.info("Admin creating book", extra={"title": request.title, "author": request.author})
    client = await get_grpc_client()
    try:
        response = await client.CreateBook(
            library_service_pb2.CreateBookRequest(
                title=request.title,
                author=request.author,
                genre=request.genre,
                published_year=request.published_year,
                available_copies=request.available_copies
            )
        )
        
        if response.success:
            logger.info("Book created successfully", extra={"book_id": response.book.book_id, "title": request.title})
            return {
                "book_id": response.book.book_id,
                "message": response.message
            }
        else:
            logger.warning("Book creation failed", extra={"title": request.title, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during book creation", extra={"title": request.title, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.put("/admin/books/{book_id}")
async def update_book(book_id: int, request: UpdateBookRequest):
    logger.info("Admin updating book", extra={"book_id": book_id, "title": request.title})
    client = await get_grpc_client()
    try:
        response = await client.UpdateBook(
            library_service_pb2.UpdateBookRequest(
                book_id=book_id,
                title=request.title,
                author=request.author,
                genre=request.genre,
                published_year=request.published_year,
                available_copies=request.available_copies
            )
        )
        
        if response.success:
            logger.info("Book updated successfully", extra={"book_id": book_id, "title": request.title})
            return {"message": response.message}
        else:
            logger.warning("Book update failed", extra={"book_id": book_id, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during book update", extra={"book_id": book_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.delete("/admin/books/{book_id}")
async def delete_book(book_id: int):
    logger.info("Admin deleting book", extra={"book_id": book_id})
    client = await get_grpc_client()
    try:
        response = await client.DeleteBook(
            library_service_pb2.GetBookRequest(book_id=book_id)
        )
        
        if response.success:
            logger.info("Book deleted successfully", extra={"book_id": book_id})
            return {"message": response.message}
        else:
            logger.warning("Book deletion failed", extra={"book_id": book_id, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during book deletion", extra={"book_id": book_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.post("/admin/users")
async def create_user(request: CreateUserRequest):
    logger.info("Admin creating user", extra={"username": request.username, "role": request.role})
    client = await get_grpc_client()
    try:
        response = await client.CreateUser(
            library_service_pb2.CreateUserRequest(
                username=request.username,
                email=request.email,
                password=request.password,
                role=request.role
            )
        )
        
        if response.success:
            logger.info("User created successfully", extra={"user_id": response.user.user_id, "username": request.username})
            return {
                "user_id": response.user.user_id,
                "message": response.message
            }
        else:
            logger.warning("User creation failed", extra={"username": request.username, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during user creation", extra={"username": request.username, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.put("/admin/users/{user_id}")
async def update_user(user_id: int, request: UpdateUserRequest):
    logger.info("Admin updating user", extra={"user_id": user_id, "username": request.username, "is_active": request.is_active})
    client = await get_grpc_client()
    try:
        response = await client.UpdateUser(
            library_service_pb2.UpdateUserRequest(
                user_id=user_id,
                username=request.username,
                email=request.email,
                role=request.role,
                is_active=request.is_active,
                password=request.password or ""
            )
        )
        
        if response.success:
            logger.info("User updated successfully", extra={"user_id": user_id, "username": request.username, "is_active": request.is_active})
            return {"message": response.message}
        else:
            logger.warning("User update failed", extra={"user_id": user_id, "reason": response.message})
            raise HTTPException(status_code=400, detail=response.message)
    except grpc.RpcError as e:
        logger.error("gRPC Error during user update", extra={"user_id": user_id, "error": str(e.details())})
        raise HTTPException(status_code=500, detail="Service unavailable")

@app.get("/")
async def root():
    return {"message": "Library API Gateway - Async Version", "grpc_backend": "localhost:50051"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)