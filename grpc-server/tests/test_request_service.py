import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.request_service import RequestService
import library_service_pb2

class TestRequestService(unittest.TestCase):
    
    def setUp(self):
        self.request_service = RequestService()
    
    @patch('services.request_service.db_pool')
    def test_create_book_request_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock request creation
        mock_cursor.fetchone.return_value = (1,)  # request_id
        
        # Create request
        request = library_service_pb2.CreateBookRequestReq(
            user_id=1,
            book_id=1,
            request_type='ISSUE',
            notes='Test request'
        )
        
        # Test create request
        response = self.request_service.create_book_request(request, None)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.message, 'Request created successfully')
    
    @patch('services.request_service.db_pool')
    def test_approve_book_request_issue(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock request data and book availability
        mock_cursor.fetchone.side_effect = [
            (1, 1, 'ISSUE', None),  # user_id, book_id, request_type, transaction_id
            (5,)  # available_copies
        ]
        
        # Create request
        request = library_service_pb2.ApproveBookRequestReq(request_id=1, admin_id=2)
        
        # Test approve request
        response = self.request_service.approve_book_request(request, None)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.message, 'Request approved successfully')
    
    @patch('services.request_service.db_pool')
    def test_reject_book_request_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock successful rejection
        mock_cursor.rowcount = 1
        
        # Create request
        request = library_service_pb2.RejectBookRequestReq(request_id=1, admin_id=2)
        
        # Test reject request
        response = self.request_service.reject_book_request(request, None)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.message, 'Request rejected successfully')

if __name__ == '__main__':
    unittest.main()