import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import grpc
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gateway import app

client = TestClient(app)

class TestInputValidation:
    """Test input validation and edge cases"""
    
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
    
    def test_issue_book_negative_book_id(self):
        response = client.post("/api/v1/admin/issue-book", json={"book_id": -1, "user_id": 1})
        assert response.status_code == 422
        assert "greater than 0" in response.json()["detail"][0]["msg"]
    
    def test_issue_book_zero_user_id(self):
        response = client.post("/api/v1/admin/issue-book", json={"book_id": 1, "user_id": 0})
        assert response.status_code == 422
        assert "greater than 0" in response.json()["detail"][0]["msg"]
    
    def test_return_book_negative_transaction_id(self):
        response = client.post("/api/v1/admin/return-book", json={"transaction_id": -1})
        assert response.status_code == 422
        assert "greater than 0" in response.json()["detail"][0]["msg"]
    
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

class TestBusinessRuleValidation:
    """Test business rule validation"""
    
    @patch('gateway.get_grpc_client')
    def test_issue_book_not_found(self, mock_grpc):
        mock_client = AsyncMock()
        mock_client.GetBooks.return_value.books = []
        mock_grpc.return_value = mock_client
        
        response = client.post("/api/v1/admin/issue-book", json={"book_id": 999, "user_id": 1})
        assert response.status_code == 404
        assert "Book not found" in response.json()["detail"]
    
    @patch('gateway.get_grpc_client')
    def test_issue_book_no_copies(self, mock_grpc):
        mock_client = AsyncMock()
        mock_book = AsyncMock()
        mock_book.book_id = 1
        mock_book.available_copies = 0
        mock_client.GetBooks.return_value.books = [mock_book]
        mock_grpc.return_value = mock_grpc
        
        response = client.post("/api/v1/admin/issue-book", json={"book_id": 1, "user_id": 1})
        assert response.status_code == 400
        assert "No copies available" in response.json()["detail"]
    
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

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @patch('gateway.get_grpc_client')
    def test_grpc_unavailable_error(self, mock_grpc):
        mock_grpc.side_effect = grpc.RpcError()
        mock_grpc.side_effect.code = lambda: grpc.StatusCode.UNAVAILABLE
        mock_grpc.side_effect.details = lambda: "Service unavailable"
        
        response = client.post("/api/v1/login", json={"username": "testuser", "password": "password123"})
        assert response.status_code == 500
        assert "Authentication service unavailable" in response.json()["detail"]
    
    @patch('gateway.get_grpc_client')
    def test_unexpected_error(self, mock_grpc):
        mock_grpc.side_effect = Exception("Unexpected error")
        
        response = client.post("/api/v1/login", json={"username": "testuser", "password": "password123"})
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    def test_user_stats_invalid_user_id(self):
        response = client.get("/api/v1/user/-1/stats")
        assert response.status_code == 400
        assert "Valid user ID required" in response.json()["detail"]
    
    def test_user_transactions_invalid_status(self):
        response = client.get("/api/v1/user/1/transactions?status=INVALID")
        assert response.status_code == 400
        assert "BORROWED, RETURNED, OVERDUE" in response.json()["detail"]
    
    def test_admin_transactions_negative_user_id(self):
        response = client.get("/api/v1/admin/transactions?user_id=-1")
        assert response.status_code == 400
        assert "non-negative" in response.json()["detail"]

class TestWebSocketValidation:
    """Test WebSocket validation"""
    
    def test_websocket_invalid_user_id_format(self):
        with client.websocket_connect("/?userId=invalid") as websocket:
            # Should close connection with error code
            pass
    
    def test_websocket_missing_user_id(self):
        with client.websocket_connect("/") as websocket:
            # Should accept but log warning
            pass

class TestSearchValidation:
    """Test search parameter validation"""
    
    def test_book_search_long_query(self):
        long_query = "x" * 201
        response = client.get(f"/api/v1/user/books/search?q={long_query}")
        assert response.status_code == 422
        assert "200" in response.json()["detail"][0]["msg"]
    
    @patch('gateway.get_grpc_client')
    def test_book_search_empty_results(self, mock_grpc):
        mock_client = AsyncMock()
        mock_client.GetBooks.return_value.books = []
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/user/books/search?q=nonexistent")
        assert response.status_code == 200
        assert response.json() == []

class TestConcurrentOperations:
    """Test concurrent operation edge cases"""
    
    @patch('gateway.get_grpc_client')
    def test_admin_book_requests_partial_data(self, mock_grpc):
        mock_client = AsyncMock()
        # Simulate missing book data
        mock_client.GetBookRequests.return_value.requests = [
            AsyncMock(request_id=1, user_id=1, book_id=999, request_type="ISSUE", status="PENDING")
        ]
        mock_client.GetBooks.return_value.books = []  # No books found
        mock_client.GetUsers.return_value.users = []  # No users found
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/admin/book-requests")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["book_title"] == "Unknown"
        assert data[0]["user_name"] == "User 1"
