from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional
from services.request_service import RequestService
from services.notification_service import notification_service
from core.grpc_client import get_grpc_client
from core.validation import validate_positive_integer, validate_request_type
import logging
import library_service_pb2

logger = logging.getLogger(__name__)
router = APIRouter()

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

@router.post('/user/book-request')
async def create_book_request(request: UserBookRequest):
    # Business rule validation
    if request.request_type == "ISSUE" and request.book_id <= 0:
        logger.warning("Issue request with invalid book_id", extra={
            "user_id": request.user_id,
            "book_id": request.book_id,
            "action": "book_request_invalid_book_id"
        })
        raise HTTPException(status_code=400, detail="Valid book ID required for issue requests")
    
    if request.request_type == "RETURN" and (not request.transaction_id or request.transaction_id <= 0):
        logger.warning("Return request without valid transaction_id", extra={
            "user_id": request.user_id,
            "transaction_id": request.transaction_id,
            "action": "book_request_invalid_transaction_id"
        })
        raise HTTPException(status_code=400, detail="Valid transaction ID required for return requests")
    
    client = await get_grpc_client()
    request_service = RequestService(client)
    return await request_service.create_book_request(
        request.user_id, request.book_id, request.request_type, 
        request.transaction_id, request.notes or ""
    )

@router.get('/admin/book-requests')
async def list_book_requests():
    client = await get_grpc_client()
    request_service = RequestService(client)
    return await request_service.get_admin_book_requests()

@router.get('/user/{user_id}/book-requests')
async def get_user_book_requests(user_id: int):
    # Input validation
    if user_id <= 0:
        logger.warning("Invalid user_id for book requests", extra={
            "user_id": user_id,
            "action": "get_user_requests_invalid_user_id"
        })
        raise HTTPException(status_code=400, detail="Valid user ID required")
    
    client = await get_grpc_client()
    request_service = RequestService(client)
    return await request_service.get_user_book_requests(user_id)

@router.post('/admin/book-requests/{request_id}/approve')
async def approve_book_request(request_id: int):
    # Input validation
    if request_id <= 0:
        logger.warning("Invalid request_id for approval", extra={
            "request_id": request_id,
            "action": "approve_invalid_request_id"
        })
        raise HTTPException(status_code=400, detail="Valid request ID required")
    
    logger.info("Book request approval initiated", extra={
        "request_id": request_id,
        "action": "request_approve_start"
    })
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
                    await notification_service.send_notification(approved_request.user_id, {
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
            logger.warning("Book request approval failed", extra={
                "request_id": request_id,
                "reason": response.message,
                "action": "request_approve_failed"
            })
            raise HTTPException(status_code=400, detail=response.message)
    except Exception as e:
        logger.error("Error during book request approval", extra={
            "request_id": request_id,
            "error": str(e)
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Service unavailable")

@router.post('/admin/book-requests/{request_id}/reject')
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
                    await notification_service.send_notification(rejected_request.user_id, {
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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Service unavailable")