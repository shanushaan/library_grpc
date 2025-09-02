import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.auth_service import AuthService

class TestAuthService:
    """Test authentication service business logic"""
    
    async def test_authenticate_user_success(self):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.user.user_id = 1
        mock_response.user.username = "testuser"
        mock_response.user.email = "test@test.com"
        mock_response.user.role = "USER"
        mock_response.message = "Success"
        
        mock_client.AuthenticateUser.return_value = mock_response
        
        auth_service = AuthService(mock_client)
        result = await auth_service.authenticate_user("testuser", "password123")
        
        assert result["user_id"] == 1
        assert result["username"] == "testuser"
        assert result["role"] == "USER"
    
    async def test_authenticate_user_failure(self):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = False
        mock_response.message = "Invalid credentials"
        
        mock_client.AuthenticateUser.return_value = mock_response
        
        auth_service = AuthService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user("testuser", "wrongpassword")
        
        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in str(exc_info.value.detail)
    
    async def test_authenticate_user_grpc_error(self):
        mock_client = AsyncMock()
        mock_client.AuthenticateUser.side_effect = Exception("gRPC error")
        
        auth_service = AuthService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user("testuser", "password123")
        
        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value.detail)