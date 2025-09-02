import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from main import app

client = TestClient(app)

class TestBookRoutes:
    """Test book management route endpoints"""
    
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
    
    @patch('routes.books.get_grpc_client')
    def test_search_books_success(self, mock_grpc):
        mock_client = AsyncMock()
        
        # Mock book with proper attributes
        mock_book = type('MockBook', (), {
            'book_id': 1,
            'title': "Test Book",
            'author': "Test Author",
            'genre': "Fiction",
            'published_year': 2023,
            'available_copies': 5
        })()
        
        mock_client.GetBooks.return_value.books = [mock_book]
        mock_grpc.return_value = mock_client
        
        response = client.get("/api/v1/user/books/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Book"
    
    @patch('routes.books.get_grpc_client')
    def test_issue_book_success(self, mock_grpc):
        mock_client = AsyncMock()
        
        # Mock book availability
        mock_book = AsyncMock()
        mock_book.book_id = 1
        mock_book.available_copies = 5
        mock_client.GetBooks.return_value.books = [mock_book]
        
        # Mock issue response
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.transaction.transaction_id = 1
        mock_response.message = "Book issued"
        mock_client.IssueBook.return_value = mock_response
        
        mock_grpc.return_value = mock_client
        
        response = client.post("/api/v1/admin/issue-book", json={"book_id": 1, "user_id": 1})
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == 1
    
    @patch('routes.books.get_grpc_client')
    def test_return_book_success(self, mock_grpc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.transaction.transaction_id = 1
        mock_response.transaction.fine_amount = 5.0
        mock_response.message = "Book returned"
        
        mock_client.ReturnBook.return_value = mock_response
        mock_grpc.return_value = mock_client
        
        response = client.post("/api/v1/admin/return-book", json={"transaction_id": 1})
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == 1
        assert data["fine_amount"] == 5.0