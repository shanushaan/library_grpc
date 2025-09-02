from fastapi import APIRouter, HTTPException
from core.grpc_client import get_grpc_client
import library_service_pb2
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get('/admin/users')
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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Service unavailable")

@router.get('/user/{user_id}/stats')
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
    except Exception as e:
        logger.error(f"Error fetching user stats: user_id={user_id} - {str(e)}")
        raise HTTPException(status_code=500, detail="Service unavailable")