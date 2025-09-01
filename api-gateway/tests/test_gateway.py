import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gateway import app

class TestAPIGateway(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        
    @patch('gateway.get_grpc_client')
    def test_login_success(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.user.user_id = 1
        mock_response.user.username = "testuser"
        mock_response.user.email = "test@test.com"
        mock_response.user.role = "USER"
        mock_response.message = "Success"
        
        mock_client.AuthenticateUser.return_value = mock_response
        
        response = self.client.post("/login", json={
            "username": "testuser",
            "password": "password123"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "testuser")
        
    @patch('gateway.get_grpc_client')
    def test_search_books(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_book = Mock()
        mock_book.book_id = 1
        mock_book.title = "Test Book"
        mock_book.author = "Test Author"
        mock_book.genre = "Fiction"
        mock_book.published_year = 2023
        mock_book.available_copies = 5
        
        mock_response = Mock()
        mock_response.books = [mock_book]
        
        mock_client.GetBooks.return_value = mock_response
        
        response = self.client.get("/user/books/search?q=test")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Test Book")
        
    @patch('gateway.get_grpc_client')
    def test_create_book_request(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.request.request_id = 1
        mock_response.request.status = "PENDING"
        mock_response.message = "Request created successfully"
        
        mock_client.CreateUserBookRequest.return_value = mock_response
        
        response = self.client.post("/user/book-request", json={
            "book_id": 1,
            "request_type": "ISSUE",
            "user_id": 1,
            "notes": "Test request"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Request created successfully")
        
    @patch('gateway.get_grpc_client')
    def test_login_invalid_credentials(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.success = False
        mock_response.message = "Invalid credentials"
        
        mock_client.AuthenticateUser.return_value = mock_response
        
        response = self.client.post("/login", json={
            "username": "invalid",
            "password": "wrong"
        })
        
        self.assertEqual(response.status_code, 401)
        
    @patch('gateway.get_grpc_client')
    def test_login_missing_fields(self, mock_grpc_client):
        response = self.client.post("/login", json={
            "username": "testuser"
            # Missing password
        })
        
        self.assertEqual(response.status_code, 422)
        
    @patch('gateway.get_grpc_client')
    def test_search_books_grpc_error(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        from grpc import RpcError
        mock_client.GetBooks.side_effect = RpcError("Service unavailable")
        
        response = self.client.get("/user/books/search?q=test")
        
        self.assertEqual(response.status_code, 500)
        
    @patch('gateway.get_grpc_client')
    def test_create_book_request_invalid_data(self, mock_grpc_client):
        response = self.client.post("/user/book-request", json={
            "book_id": "invalid",  # Should be int
            "request_type": "ISSUE",
            "user_id": 1
        })
        
        self.assertEqual(response.status_code, 422)
        
    @patch('gateway.get_grpc_client')
    def test_create_book_request_grpc_failure(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.success = False
        mock_response.message = "Book not available"
        
        mock_client.CreateUserBookRequest.return_value = mock_response
        
        response = self.client.post("/user/book-request", json={
            "book_id": 1,
            "request_type": "ISSUE",
            "user_id": 1
        })
        
        self.assertEqual(response.status_code, 400)
        
    @patch('gateway.get_grpc_client')
    def test_approve_request_not_found(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.success = False
        mock_response.message = "Request not found"
        
        mock_client.ApproveBookRequest.return_value = mock_response
        
        response = self.client.post("/admin/book-requests/999/approve")
        
        self.assertEqual(response.status_code, 400)
        
    @patch('gateway.get_grpc_client')
    def test_reject_request_not_found(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.success = False
        mock_response.message = "Request not found"
        
        mock_client.RejectBookRequest.return_value = mock_response
        
        response = self.client.post("/admin/book-requests/999/reject")
        
        self.assertEqual(response.status_code, 400)
        
    @patch('gateway.get_grpc_client')
    def test_issue_book_invalid_user(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.success = False
        mock_response.message = "User not found"
        
        mock_client.IssueBook.return_value = mock_response
        
        response = self.client.post("/admin/issue-book", json={
            "book_id": 1,
            "user_id": 999
        })
        
        self.assertEqual(response.status_code, 400)
        
    @patch('gateway.get_grpc_client')
    def test_return_book_invalid_transaction(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.success = False
        mock_response.message = "Transaction not found"
        
        mock_client.ReturnBook.return_value = mock_response
        
        response = self.client.post("/admin/return-book", json={
            "transaction_id": 999
        })
        
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()