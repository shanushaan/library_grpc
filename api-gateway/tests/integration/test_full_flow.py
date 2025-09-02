import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from main import app

client = TestClient(app)

class TestFullFlow:
    """Test complete user flows end-to-end"""
    
    @patch('routes.auth.get_grpc_client')
    @patch('routes.requests.get_grpc_client')
    def test_login_and_create_request_flow(self, mock_request_grpc, mock_auth_grpc):
        # Mock login
        mock_auth_client = AsyncMock()
        mock_auth_response = AsyncMock()
        mock_auth_response.success = True
        mock_auth_response.user.user_id = 1
        mock_auth_response.user.username = "testuser"
        mock_auth_response.user.email = "test@test.com"
        mock_auth_response.user.role = "USER"
        mock_auth_response.message = "Success"
        
        mock_auth_client.AuthenticateUser.return_value = mock_auth_response
        mock_auth_grpc.return_value = mock_auth_client
        
        # Mock book request
        mock_request_client = AsyncMock()
        mock_request_response = AsyncMock()
        mock_request_response.success = True
        mock_request_response.request.request_id = 1
        mock_request_response.request.status = "PENDING"
        mock_request_response.message = "Request created"
        
        mock_request_client.CreateUserBookRequest.return_value = mock_request_response
        mock_request_grpc.return_value = mock_request_client
        
        # Test login
        login_response = client.post("/api/v1/login", json={
            "username": "testuser",
            "password": "password123"
        })
        assert login_response.status_code == 200
        
        # Test book request
        request_response = client.post("/api/v1/user/book-request", json={
            "book_id": 1,
            "request_type": "ISSUE",
            "user_id": 1,
            "notes": "Test request"
        })
        assert request_response.status_code == 200
        assert request_response.json()["request_id"] == 1