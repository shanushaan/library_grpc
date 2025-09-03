import hashlib
from datetime import datetime
import logging
import psycopg2
from connection_pool import db_pool
import library_service_pb2

logger = logging.getLogger(__name__)

class AuthService:
    
    def authenticate_user(self, request, context):
        """Authenticate user with username and password"""
        logger.info("Authentication attempt", extra={"username": request.username, "method": "AuthenticateUser"})
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    password_hash = hashlib.sha256(request.password.encode()).hexdigest()
                    cursor.execute(
                        "SELECT user_id, username, email, role, is_active FROM users WHERE username = %s AND password_hash = %s AND is_active = true",
                        (request.username, password_hash)
                    )
                    user_data = cursor.fetchone()
                    
                    if user_data:
                        cursor.execute(
                            "UPDATE users SET last_login = %s WHERE user_id = %s",
                            (datetime.utcnow(), user_data[0])
                        )
                        conn.commit()
                        logger.info("Authentication successful", extra={"username": request.username, "role": user_data[3], "user_id": user_data[0]})
                        
                        return library_service_pb2.AuthResponse(
                            success=True,
                            user=library_service_pb2.User(
                                user_id=user_data[0],
                                username=user_data[1],
                                email=user_data[2],
                                role=user_data[3],
                                is_active=user_data[4]
                            ),
                            message="Authentication successful"
                        )
                    else:
                        logger.warning("Authentication failed", extra={"username": request.username, "reason": "invalid_credentials"})
                        return library_service_pb2.AuthResponse(
                            success=False,
                            message="Invalid credentials"
                        )
        except psycopg2.DatabaseError as e:
            logger.error("Database error during authentication", extra={"username": request.username, "error": str(e)})
            raise
        except Exception as e:
            logger.error("Error during authentication", extra={"username": request.username, "error": str(e), "error_type": "unexpected_error"})
            raise