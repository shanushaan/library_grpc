import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.auth_service import AuthService
import library_service_pb2

class TestAuthService(unittest.TestCase):
    
    def setUp(self):
        self.auth_service = AuthService()
    
    @patch('services.auth_service.db_pool')
    def test_authenticate_user_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock user data
        mock_cursor.fetchone.return_value = (1, 'testuser', 'test@test.com', 'USER', True)
        
        # Create request
        request = library_service_pb2.AuthRequest(username='testuser', password='password')
        
        # Test authentication
        response = self.auth_service.authenticate_user(request, None)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.user.username, 'testuser')
        self.assertEqual(response.message, 'Authentication successful')
    
    @patch('services.auth_service.db_pool')
    def test_authenticate_user_invalid_credentials(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock no user found
        mock_cursor.fetchone.return_value = None
        
        # Create request
        request = library_service_pb2.AuthRequest(username='invalid', password='wrong')
        
        # Test authentication
        response = self.auth_service.authenticate_user(request, None)
        
        # Assertions
        self.assertFalse(response.success)
        self.assertEqual(response.message, 'Invalid credentials')

if __name__ == '__main__':
    unittest.main()