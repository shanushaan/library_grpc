import grpc
import library_service_pb2
import library_service_pb2_grpc
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class BookService:
    def __init__(self, grpc_client):
        self.client = grpc_client
    
    async def search_books(self, query: str = ""):
        """Search books by query"""
        logger.info("Book search initiated", extra={"query": query, "action": "book_search_start"})
        
        try:
            logger.debug("Sending book search request to gRPC server", extra={"query": query})
            response = await self.client.GetBooks(
                library_service_pb2.GetBooksRequest(search_query=query)
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
                "query": query,
                "results_count": len(books),
                "action": "book_search_success"
            })
            return books
            
        except grpc.RpcError as e:
            logger.error("gRPC service error during book search", extra={
                "query": query,
                "grpc_code": e.code().name,
                "grpc_details": str(e.details()),
                "error_type": "grpc_error",
                "action": "book_search_grpc_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Book search service unavailable")
        except Exception as e:
            logger.error("Unexpected error during book search", extra={
                "query": query,
                "error": str(e),
                "error_type": "unexpected_error",
                "action": "book_search_unexpected_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def issue_book(self, book_id: int, user_id: int):
        """Issue book to user with validation"""
        logger.info("Book issue initiated", extra={
            "book_id": book_id,
            "user_id": user_id,
            "action": "book_issue_start"
        })
        
        # Validate book exists and is available
        try:
            books_response = await self.client.GetBooks(library_service_pb2.GetBooksRequest(search_query=""))
            book = next((b for b in books_response.books if b.book_id == book_id), None)
            
            if not book:
                logger.warning("Book issue failed - book not found", extra={
                    "book_id": book_id,
                    "action": "book_issue_book_not_found"
                })
                raise HTTPException(status_code=404, detail="Book not found")
            
            if book.available_copies <= 0:
                logger.warning("Book issue failed - no copies available", extra={
                    "book_id": book_id,
                    "available_copies": book.available_copies,
                    "action": "book_issue_no_copies"
                })
                raise HTTPException(status_code=400, detail="No copies available for this book")
            
            logger.debug("Sending book issue request to gRPC server", extra={
                "book_id": book_id,
                "user_id": user_id
            })
            response = await self.client.IssueBook(
                library_service_pb2.IssueBookRequest(
                    book_id=book_id,
                    member_id=user_id,
                    admin_id=1  # TODO: Get from auth
                )
            )
            
            if response.success:
                logger.info("Book issued successfully", extra={
                    "book_id": book_id,
                    "user_id": user_id,
                    "transaction_id": response.transaction.transaction_id,
                    "action": "book_issue_success"
                })
                return {
                    "transaction_id": response.transaction.transaction_id,
                    "message": response.message
                }
            else:
                logger.warning("Book issue failed", extra={
                    "book_id": book_id,
                    "user_id": user_id,
                    "reason": response.message,
                    "action": "book_issue_failed"
                })
                raise HTTPException(status_code=400, detail=response.message)
                
        except HTTPException:
            raise
        except grpc.RpcError as e:
            logger.error("gRPC service error during book issue", extra={
                "book_id": book_id,
                "user_id": user_id,
                "grpc_code": e.code().name,
                "grpc_details": str(e.details()),
                "error_type": "grpc_error",
                "action": "book_issue_grpc_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Book issue service unavailable")
        except Exception as e:
            logger.error("Unexpected error during book issue", extra={
                "book_id": book_id,
                "user_id": user_id,
                "error": str(e),
                "error_type": "unexpected_error",
                "action": "book_issue_unexpected_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def return_book(self, transaction_id: int):
        """Return book by transaction ID"""
        logger.info("Book return initiated", extra={
            "transaction_id": transaction_id,
            "action": "book_return_start"
        })
        
        try:
            logger.debug("Sending book return request to gRPC server", extra={"transaction_id": transaction_id})
            response = await self.client.ReturnBook(
                library_service_pb2.ReturnBookRequest(
                    transaction_id=transaction_id,
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
                    "transaction_id": transaction_id,
                    "reason": response.message,
                    "action": "book_return_failed"
                })
                raise HTTPException(status_code=400, detail=response.message)
                
        except grpc.RpcError as e:
            logger.error("gRPC service error during book return", extra={
                "transaction_id": transaction_id,
                "grpc_code": e.code().name,
                "grpc_details": str(e.details()),
                "error_type": "grpc_error",
                "action": "book_return_grpc_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Book return service unavailable")
        except Exception as e:
            logger.error("Unexpected error during book return", extra={
                "transaction_id": transaction_id,
                "error": str(e),
                "error_type": "unexpected_error",
                "action": "book_return_unexpected_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")