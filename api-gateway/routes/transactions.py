from fastapi import APIRouter, HTTPException
from core.grpc_client import get_grpc_client
import library_service_pb2
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get('/admin/transactions')
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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@router.get('/user/{user_id}/transactions')
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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Service unavailable")