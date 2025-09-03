import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.transaction_service import TransactionService
import library_service_pb2

class TestTransactionService(unittest.TestCase):
    
    def setUp(self):
        self.transaction_service = TransactionService()
    
    @patch('services.transaction_service.db_pool')
    def test_issue_book_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock database responses
        mock_cursor.fetchone.side_effect = [
            (5,),  # Book availability
            ('user',),  # User role
            (0,),  # No existing borrow
            (2,),  # Current borrowed count
            (1,)   # Transaction ID
        ]
        
        # Create request
        request = library_service_pb2.IssueBookRequest(book_id=1, member_id=1)
        
        # Test issue book
        response = self.transaction_service.issue_book(request, None)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.message, 'Book issued successfully')
    
    @patch('services.transaction_service.db_pool')
    def test_issue_book_not_available(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock no available copies
        mock_cursor.fetchone.return_value = (0,)
        
        # Create request
        request = library_service_pb2.IssueBookRequest(book_id=1, member_id=1)
        
        # Test issue book
        response = self.transaction_service.issue_book(request, None)
        
        # Assertions
        self.assertFalse(response.success)
        self.assertEqual(response.message, 'Book not available')
    
    @patch('services.transaction_service.db_pool')
    def test_return_book_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock transaction data
        from datetime import datetime, timedelta
        due_date = datetime.utcnow() + timedelta(days=5)
        mock_cursor.fetchone.return_value = (1, due_date)  # book_id, due_date
        
        # Create request
        request = library_service_pb2.ReturnBookRequest(transaction_id=1)
        
        # Test return book
        response = self.transaction_service.return_book(request, None)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.message, 'Book returned successfully')

if __name__ == '__main__':
    unittest.main()