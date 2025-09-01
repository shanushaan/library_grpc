import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gateway import app

class TestAPIGatewayEdgeCases(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        
    def test_invalid_json_payload(self):
        response = self.client.post("/login", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 422)
        
    def test_missing_content_type(self):
        response = self.client.post("/login", data='{"username":"test"}')
        
        self.assertEqual(response.status_code, 422)
        
    @patch('gateway.get_grpc_client')
    def test_grpc_timeout_error(self, mock_grpc_client):
        import grpc
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        mock_client.AuthenticateUser.side_effect = grpc.RpcError("Timeout")
        
        response = self.client.post("/login", json={
            "username": "testuser",
            "password": "password123"
        })
        
        self.assertEqual(response.status_code, 500)
        
    def test_invalid_book_id_type(self):
        response = self.client.post("/user/book-request", json={
            "book_id": "not_a_number",
            "request_type": "ISSUE",
            "user_id": 1
        })
        
        self.assertEqual(response.status_code, 422)
        
    def test_invalid_user_id_type(self):
        response = self.client.post("/user/book-request", json={
            "book_id": 1,
            "request_type": "ISSUE",
            "user_id": "not_a_number"
        })
        
        self.assertEqual(response.status_code, 422)
        
    def test_empty_request_body(self):
        response = self.client.post("/login", json={})
        
        self.assertEqual(response.status_code, 422)
        
    def test_invalid_request_type(self):
        response = self.client.post("/user/book-request", json={
            "book_id": 1,
            "request_type": "INVALID_TYPE",
            "user_id": 1
        })
        
        # Should still pass validation but might fail at business logic level
        self.assertIn(response.status_code, [200, 400, 500])
        
    @patch('gateway.get_grpc_client')
    def test_admin_requests_empty_response(self, mock_grpc_client):
        mock_client = Mock()
        mock_grpc_client.return_value = mock_client
        
        # Mock empty responses
        mock_requests_response = Mock()
        mock_requests_response.requests = []
        
        mock_books_response = Mock()
        mock_books_response.books = []
        
        mock_users_response = Mock()
        mock_users_response.users = []
        
        mock_client.GetBookRequests.return_value = mock_requests_response
        mock_client.GetBooks.return_value = mock_books_response
        mock_client.GetUsers.return_value = mock_users_response
        
        response = self.client.get("/admin/book-requests")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)
        
    def test_invalid_path_parameter(self):
        response = self.client.post("/admin/book-requests/invalid_id/approve")
        
        self.assertEqual(response.status_code, 422)
        
    def test_negative_book_id(self):
        response = self.client.post("/user/book-request", json={
            "book_id": -1,
            "request_type": "ISSUE",
            "user_id": 1
        })
        
        # Should pass validation but might fail at business logic
        self.assertIn(response.status_code, [200, 400, 500])

if __name__ == '__main__':
    unittest.main()