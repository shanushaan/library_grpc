import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from main import app

client = TestClient(app)

class TestAuthRoutes:
    """Test authentication route endpoints"""
    
    def test_login_empty_username(self):
        response = client.post("/api/v1/login", json={"username": "", "password": "password123"})
        assert response.status_code == 422
        assert "at least 3 characters" in response.json()["detail"][0]["msg"]
    
    def test_login_short_password(self):
        response = client.post("/api/v1/login", json={"username": "testuser", "password": "123"})
        assert response.status_code == 422
        assert "at least 6 characters" in response.json()["detail"][0]["msg"]
    
    def test_login_invalid_username_format(self):
        response = client.post("/api/v1/login", json={"username": "test@user", "password": "password123"})
        assert response.status_code == 422
        assert "letters, numbers, and underscores" in response.json()["detail"][0]["msg"]
    
    @patch('routes.auth.get_grpc_client')
    def test_login_success(self, mock_grpc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.user.user_id = 1
        mock_response.user.username = "testuser"
        mock_response.user.email = "test@test.com"
        mock_response.user.role = "USER"
        mock_response.message = "Success"
        
        mock_client.AuthenticateUser.return_value = mock_response
        mock_grpc.return_value = mock_client
        
        response = client.post("/api/v1/login", json={
            "username": "testuser",
            "password": "password123"
        })
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"