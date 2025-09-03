import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.request_service import RequestService

pytestmark = pytest.mark.asyncio

class TestAdminRestrictions:
    """Test admin user restrictions for book requests"""
    
    async def test_admin_cannot_request_book_issue(self):
        mock_client = AsyncMock()
        
        # Mock admin user
        mock_user = type('MockUser', (), {
            'user_id': 5,
            'username': "admin",
            'role': "ADMIN"
        })()
        mock_client.GetUsers.return_value.users = [mock_user]
        
        request_service = RequestService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await request_service.create_book_request(5, 1, "ISSUE", None, "Test")
        
        assert exc_info.value.status_code == 403
        assert "Admin users cannot request book issues" in str(exc_info.value.detail)
    
    async def test_admin_can_request_book_return(self):
        mock_client = AsyncMock()
        
        # Mock admin user
        mock_user = type('MockUser', (), {
            'user_id': 5,
            'username': "admin", 
            'role': "ADMIN"
        })()
        mock_client.GetUsers.return_value.users = [mock_user]
        
        # Mock successful return request
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.request.request_id = 1
        mock_response.request.status = "PENDING"
        mock_response.message = "Return request created"
        mock_client.CreateUserBookRequest.return_value = mock_response
        
        request_service = RequestService(mock_client)
        result = await request_service.create_book_request(5, 0, "RETURN", 1, "Return book")
        
        assert result["request_id"] == 1
        assert result["status"] == "PENDING"
    
    async def test_regular_user_can_request_book_issue(self):
        mock_client = AsyncMock()
        
        # Mock regular user
        mock_user = type('MockUser', (), {
            'user_id': 3,
            'username': "user",
            'role': "USER"
        })()
        mock_client.GetUsers.return_value.users = [mock_user]
        
        # Mock successful issue request
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.request.request_id = 2
        mock_response.request.status = "PENDING"
        mock_response.message = "Issue request created"
        mock_client.CreateUserBookRequest.return_value = mock_response
        
        request_service = RequestService(mock_client)
        result = await request_service.create_book_request(3, 1, "ISSUE", None, "Issue book")
        
        assert result["request_id"] == 2
        assert result["status"] == "PENDING"