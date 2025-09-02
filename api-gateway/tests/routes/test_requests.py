import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from main import app

client = TestClient(app)

class TestRequestRoutes:
    """Test request management route endpoints"""
    
    def test_book_request_invalid_type(self):
        response = client.post("/api/v1/user/book-request", json={
            "book_id": 1, "request_type": "INVALID", "user_id": 1
        })
        assert response.status_code == 422
        assert "ISSUE, RETURN" in response.json()["detail"][0]["msg"]
    
    def test_book_request_long_notes(self):
        long_notes = "x" * 501
        response = client.post("/api/v1/user/book-request", json={
            "book_id": 1, "request_type": "ISSUE", "user_id": 1, "notes": long_notes
        })
        assert response.status_code == 422
        assert "500" in response.json()["detail"][0]["msg"]
    
    def test_book_request_issue_without_book_id(self):
        response = client.post("/api/v1/user/book-request", json={
            "book_id": 0, "request_type": "ISSUE", "user_id": 1
        })
        assert response.status_code == 400
        assert "Valid book ID required" in response.json()["detail"]
    
    def test_book_request_return_without_transaction_id(self):
        response = client.post("/api/v1/user/book-request", json={
            "book_id": 0, "request_type": "RETURN", "user_id": 1
        })
        assert response.status_code == 400
        assert "Valid transaction ID required" in response.json()["detail"]
    
    def test_approve_request_invalid_id(self):
        response = client.post("/api/v1/admin/book-requests/-1/approve")
        assert response.status_code == 400
        assert "Valid request ID required" in response.json()["detail"]
    
    def test_reject_request_invalid_id(self):
        response = client.post("/api/v1/admin/book-requests/0/reject", json={"notes": "test"})
        assert response.status_code == 400
        assert "Valid request ID required" in response.json()["detail"]
    
    @patch('routes.requests.get_grpc_client')
    def test_list_book_requests_success(self, mock_grpc):
        mock_client = AsyncMock()
        
        # Mock request with proper attributes
        mock_request = type('MockRequest', (), {
            'request_id': 1,
            'user_id': 1,
            'book_id': 1,
            'request_type': "ISSUE",
            'status': "PENDING",
            'request_date': "2023-01-01",
            'notes': "Test request"
        })()
        
        mock_client.GetBookRequests.return_value.requests = [mock_request]
        mock_client.GetBooks.return_value.books = []
        mock_client.GetUsers.return_value.users = []
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/admin/book-requests")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["request_id"] == 1
    
    @patch('routes.requests.get_grpc_client')
    def test_get_user_book_requests_success(self, mock_grpc):
        mock_client = AsyncMock()
        
        # Mock request with proper attributes
        mock_request = type('MockUserRequest', (), {
            'request_id': 1,
            'user_id': 1,
            'book_id': 1,
            'request_type': "ISSUE",
            'status': "PENDING",
            'request_date': "2023-01-01",
            'notes': "Test request",
            'transaction_id': 0
        })()
        
        mock_client.GetBookRequests.return_value.requests = [mock_request]
        mock_client.GetBooks.return_value.books = []
        mock_client.GetTransactions.return_value.transactions = []
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/user/1/book-requests")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["request_id"] == 1
    
    @patch('routes.requests.get_grpc_client')
    def test_approve_request_success(self, mock_grpc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.message = "Approved"
        
        mock_client.ApproveBookRequest.return_value = mock_response
        mock_client.GetBookRequests.return_value.requests = []
        mock_grpc.return_value = mock_client
        
        response = client.post("/api/v1/admin/book-requests/1/approve")
        assert response.status_code == 200
        assert response.json()["message"] == "Approved"
    
    @patch('routes.requests.get_grpc_client')
    def test_reject_request_success(self, mock_grpc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.message = "Rejected"
        
        mock_client.RejectBookRequest.return_value = mock_response
        mock_client.GetBookRequests.return_value.requests = []
        mock_grpc.return_value = mock_client
        
        response = client.post("/api/v1/admin/book-requests/1/reject", json={"notes": "test"})
        assert response.status_code == 200
        assert response.json()["message"] == "Rejected"