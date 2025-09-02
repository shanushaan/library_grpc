import grpc
import library_service_pb2
import library_service_pb2_grpc
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, grpc_client):
        self.client = grpc_client
    
    async def authenticate_user(self, username: str, password: str):
        """Authenticate user credentials"""
        logger.info("Authentication attempt initiated", extra={
            "username": username, 
            "action": "auth_start"
        })
        
        try:
            logger.debug("Sending authentication request to gRPC server", extra={"username": username})
            response = await self.client.AuthenticateUser(
                library_service_pb2.AuthRequest(
                    username=username,
                    password=password
                )
            )
            
            if response.success:
                logger.info("Authentication successful", extra={
                    "username": username,
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
                    "username": username,
                    "reason": response.message,
                    "action": "auth_failed"
                })
                raise HTTPException(status_code=401, detail=response.message)
                
        except grpc.RpcError as e:
            logger.error("gRPC service error during authentication", extra={
                "username": username,
                "grpc_code": e.code().name,
                "grpc_details": str(e.details()),
                "error_type": "grpc_error",
                "action": "auth_grpc_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Authentication service unavailable")
        except Exception as e:
            logger.error("Unexpected error during authentication", extra={
                "username": username,
                "error": str(e),
                "error_type": "unexpected_error",
                "action": "auth_unexpected_error"
            }, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")