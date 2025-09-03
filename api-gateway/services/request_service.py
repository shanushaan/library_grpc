import grpc
import library_service_pb2
import library_service_pb2_grpc
from fastapi import HTTPException
import logging
import asyncio
from core.enums import RequestType, RequestStatus, UserRole

logger = logging.getLogger(__name__)

class RequestService:
    def __init__(self, grpc_client):
        self.client = grpc_client
    
    async def create_book_request(self, user_id: int, book_id: int, request_type: str, transaction_id: int = None, notes: str = ""):
        """Create user book request"""
        logger.info("User book request initiated", extra={
            "user_id": user_id,
            "book_id": book_id,
            "request_type": request_type,
            "transaction_id": transaction_id,
            "action": "user_book_request_start"
        })
        
        try:
            # Check if user is admin and trying to create ISSUE request
            if request_type == RequestType.ISSUE.value:
                user_response = await self.client.GetUsers(library_service_pb2.GetUsersRequest())
                for user in user_response.users:
                    if user.user_id == user_id and user.role == UserRole.ADMIN.value:
                        raise HTTPException(status_code=403, detail="Admin users cannot request book issues")
            
            logger.debug("Sending book request to gRPC server", extra={
                "user_id": user_id,
                "book_id": book_id,
                "request_type": request_type
            })
            response = await self.client.CreateUserBookRequest(
                library_service_pb2.CreateBookRequestReq(
                    user_id=user_id,
                    book_id=book_id,
                    request_type=request_type,
                    transaction_id=transaction_id or 0,
                    notes=notes
                )
            )
            
            if response.success:
                logger.info("User book request created successfully", extra={
                    "user_id": user_id,
                    "book_id": book_id,
                    "request_type": request_type,
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
                    "user_id": user_id,
                    "book_id": book_id,
                    "request_type": request_type,
                    "reason": response.message,
                    "action": "user_book_request_failed"
                })
                raise HTTPException(status_code=400, detail=response.message)
                
        except HTTPException:
            raise
        except grpc.RpcError as e:
            logger.error("gRPC service error during book request", extra={
                "user_id": user_id,
                "book_id": book_id,
                "request_type": request_type,
                "grpc_code": e.code().name,
                "grpc_details": str(e.details()),
                "error_type": "grpc_error",
                "action": "user_book_request_grpc_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Book request service unavailable")
        except Exception as e:
            logger.error("Unexpected error during book request", extra={
                "user_id": user_id,
                "book_id": book_id,
                "request_type": request_type,
                "error": str(e),
                "error_type": "unexpected_error",
                "action": "user_book_request_unexpected_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_admin_book_requests(self):
        """Get all pending book requests for admin"""
        logger.info("Admin book requests list initiated", extra={"action": "admin_book_requests_start"})
        
        try:
            logger.debug("Fetching concurrent data: requests, books, users")
            # Get all data concurrently
            requests_task = self.client.GetBookRequests(library_service_pb2.GetBookRequestsReq(status=RequestStatus.PENDING.value))
            books_task = self.client.GetBooks(library_service_pb2.GetBooksRequest(search_query=""))
            users_task = self.client.GetUsers(library_service_pb2.GetUsersRequest())
            
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
    
    async def get_user_book_requests(self, user_id: int):
        """Get book requests for specific user"""
        logger.info("Fetching book requests for user", extra={
            "user_id": user_id,
            "action": "user_book_requests_start"
        })
        
        try:
            response = await self.client.GetBookRequests(
                library_service_pb2.GetBookRequestsReq(status="")
            )
            
            # Get books and transactions for additional info
            books_response = await self.client.GetBooks(
                library_service_pb2.GetBooksRequest(search_query="")
            )
            transactions_response = await self.client.GetTransactions(
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
                    
                    if req.request_type == RequestType.RETURN.value and req.transaction_id and req.transaction_id > 0:
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
            
            logger.info("User book requests retrieved successfully", extra={
                "user_id": user_id,
                "total_requests": len(user_requests),
                "action": "user_book_requests_success"
            })
            return user_requests
            
        except grpc.RpcError as e:
            logger.error("gRPC service error during user book requests fetch", extra={
                "user_id": user_id,
                "grpc_code": e.code().name,
                "grpc_details": str(e.details()),
                "error_type": "grpc_error",
                "action": "user_book_requests_grpc_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Book requests service unavailable")
        except Exception as e:
            logger.error("Unexpected error during user book requests fetch", extra={
                "user_id": user_id,
                "error": str(e),
                "error_type": "unexpected_error",
                "action": "user_book_requests_unexpected_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")