import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.user_service import UserService
import library_service_pb2

class TestUserService(unittest.TestCase):
    
    def setUp(self):
        self.user_service = UserService()
    
    @patch('services.user_service.db_pool')
    def test_get_users_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock user data
        mock_cursor.fetchall.return_value = [
            (1, 'user1', 'user1@test.com', 'USER', True),
            (2, 'admin', 'admin@test.com', 'ADMIN', True)
        ]
        
        # Create request
        request = library_service_pb2.GetUsersRequest()
        
        # Test get users
        response = self.user_service.get_users(request, None)
        
        # Assertions
        self.assertEqual(len(response.users), 2)
        self.assertEqual(response.users[0].username, 'user1')
        self.assertEqual(response.users[1].role, 'ADMIN')
    
    @patch('services.user_service.db_pool')
    def test_create_user_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock user creation
        mock_cursor.fetchone.return_value = (1,)  # user_id
        
        # Create request
        request = library_service_pb2.CreateUserRequest(
            username='newuser',
            email='new@test.com',
            password='password',
            role='USER'
        )
        
        # Test create user
        response = self.user_service.create_user(request, None)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.user.username, 'newuser')
        self.assertEqual(response.message, 'User created successfully')
    
    @patch('services.user_service.db_pool')
    def test_get_user_stats_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock stats data
        mock_cursor.fetchone.side_effect = [
            (10,),  # total_taken
            (2,),   # currently_borrowed
            (1, 50) # overdue_books, total_fine
        ]
        
        # Create request
        request = library_service_pb2.UserStatsRequest(user_id=1)
        
        # Test get user stats
        response = self.user_service.get_user_stats(request, None)
        
        # Assertions
        self.assertEqual(response.total_books_taken, 10)
        self.assertEqual(response.currently_borrowed, 2)
        self.assertEqual(response.overdue_books, 1)
        self.assertEqual(response.total_fine, 50)

if __name__ == '__main__':
    unittest.main()