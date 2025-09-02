import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from main import app

client = TestClient(app)

class TestUserRoutes:
    """Test user management route endpoints"""
    
    @patch('routes.users.get_grpc_client')
    def test_list_users_success(self, mock_grpc):
        mock_client = AsyncMock()
        mock_user = AsyncMock()
        mock_user.user_id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@test.com"
        mock_user.role = "USER"
        mock_user.is_active = True
        
        mock_client.GetUsers.return_value.users = [mock_user]
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/admin/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["username"] == "testuser"
    
    @patch('routes.users.get_grpc_client')
    def test_list_users_service_error(self, mock_grpc):
        mock_client = AsyncMock()
        mock_client.GetUsers.side_effect = Exception("Service error")
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/admin/users")
        assert response.status_code == 500
        assert "Service unavailable" in response.json()["detail"]
    
    def test_get_user_stats_invalid_user_id(self):
        response = client.get("/api/v1/user/-1/stats")
        assert response.status_code == 400
        assert "Valid user ID required" in response.json()["detail"]
    
    def test_get_user_stats_zero_user_id(self):
        response = client.get("/api/v1/user/0/stats")
        assert response.status_code == 400
        assert "Valid user ID required" in response.json()["detail"]
    
    @patch('routes.users.get_grpc_client')
    def test_get_user_stats_success(self, mock_grpc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.total_books_taken = 5
        mock_response.currently_borrowed = 2
        mock_response.overdue_books = 1
        mock_response.total_fine = 10.50
        
        mock_client.GetUserStats.return_value = mock_response
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/user/1/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_books_taken"] == 5
        assert data["currently_borrowed"] == 2
        assert data["overdue_books"] == 1
        assert data["total_fine"] == 10.50
    
    @patch('routes.users.get_grpc_client')
    def test_get_user_stats_service_error(self, mock_grpc):
        mock_client = AsyncMock()
        mock_client.GetUserStats.side_effect = Exception("Service error")
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/user/1/stats")
        assert response.status_code == 500
        assert "Service unavailable" in response.json()["detail"]

class TestTransactionRoutes:
    """Test transaction management route endpoints"""
    
    def test_admin_transactions_negative_user_id(self):
        response = client.get("/api/v1/admin/transactions?user_id=-1")
        assert response.status_code == 400
        assert "non-negative" in response.json()["detail"]
    
    def test_admin_transactions_invalid_status(self):
        response = client.get("/api/v1/admin/transactions?status=INVALID")
        assert response.status_code == 400
        assert "BORROWED, RETURNED, OVERDUE" in response.json()["detail"]
    
    @patch('routes.transactions.get_grpc_client')
    def test_admin_transactions_success(self, mock_grpc):
        mock_client = AsyncMock()
        
        # Mock transaction with proper attributes
        mock_transaction = type('MockTransaction', (), {
            'transaction_id': 1,
            'member_id': 1,
            'book_id': 1,
            'transaction_type': "ISSUE",
            'transaction_date': "2023-01-01",
            'due_date': "2023-01-15",
            'return_date': "",
            'status': "BORROWED",
            'fine_amount': 0.0
        })()
        
        # Mock user with proper attributes
        mock_user = type('MockUser', (), {
            'user_id': 1,
            'username': "testuser"
        })()
        
        # Mock book with proper attributes
        mock_book = type('MockBook', (), {
            'book_id': 1,
            'title': "Test Book"
        })()
        
        mock_client.GetTransactions.return_value.transactions = [mock_transaction]
        mock_client.GetUsers.return_value.users = [mock_user]
        mock_client.GetBooks.return_value.books = [mock_book]
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/admin/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["transaction_id"] == 1
        assert data[0]["username"] == "testuser"
        assert data[0]["book_title"] == "Test Book"
    
    @patch('routes.transactions.get_grpc_client')
    def test_admin_transactions_service_error(self, mock_grpc):
        mock_client = AsyncMock()
        mock_client.GetTransactions.side_effect = Exception("Service error")
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/admin/transactions")
        assert response.status_code == 500
        assert "Service unavailable" in response.json()["detail"]
    
    def test_user_transactions_invalid_user_id(self):
        response = client.get("/api/v1/user/-1/transactions")
        assert response.status_code == 400
        assert "Valid user ID required" in response.json()["detail"]
    
    def test_user_transactions_invalid_status(self):
        response = client.get("/api/v1/user/1/transactions?status=INVALID")
        assert response.status_code == 400
        assert "BORROWED, RETURNED, OVERDUE" in response.json()["detail"]
    
    @patch('routes.transactions.get_grpc_client')
    def test_user_transactions_success(self, mock_grpc):
        mock_client = AsyncMock()
        
        # Mock transaction with proper attributes
        mock_transaction = type('MockUserTransaction', (), {
            'transaction_id': 1,
            'book_id': 1,
            'book_title': "Test Book",
            'book_author': "Test Author",
            'transaction_type': "ISSUE",
            'transaction_date': "2023-01-01",
            'due_date': "2023-01-15",
            'return_date': "",
            'status': "BORROWED",
            'fine_amount': 0.0
        })()
        
        mock_client.GetUserTransactions.return_value.transactions = [mock_transaction]
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/user/1/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["transaction_id"] == 1
        assert data[0]["book_title"] == "Test Book"
    
    @patch('routes.transactions.get_grpc_client')
    def test_user_transactions_service_error(self, mock_grpc):
        mock_client = AsyncMock()
        mock_client.GetUserTransactions.side_effect = Exception("Service error")
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/user/1/transactions")
        assert response.status_code == 500
        assert "Service unavailable" in response.json()["detail"]