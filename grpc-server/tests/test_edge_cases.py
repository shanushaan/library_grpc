import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.library_service import LibraryServiceImpl
import library_service_pb2

class TestLibraryServiceEdgeCases(unittest.TestCase):
    
    def setUp(self):
        self.service = LibraryServiceImpl()
        
    @patch('services.library_service.SessionLocal')
    def test_database_connection_error(self, mock_session):
        mock_session.side_effect = Exception("Database connection failed")
        
        request = library_service_pb2.AuthRequest(
            username="testuser",
            password="password123"
        )
        
        with self.assertRaises(Exception):
            self.service.AuthenticateUser(request, None)
            
    @patch('services.library_service.SessionLocal')
    def test_empty_book_search(self, mock_session):
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_db.query.return_value.all.return_value = []
        
        request = library_service_pb2.GetBooksRequest(search_query="nonexistent")
        response = self.service.GetBooks(request, None)
        
        self.assertEqual(len(response.books), 0)
        
    @patch('services.library_service.SessionLocal')
    def test_approve_request_book_unavailable(self, mock_session):
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        mock_request = Mock()
        mock_request.request_type = "ISSUE"
        mock_request.book_id = 1
        mock_request.user_id = 1
        
        mock_book = Mock()
        mock_book.available_copies = 0
        
        def query_side_effect(model):
            if hasattr(model, '__name__') and 'BookRequest' in str(model):
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_request))))
            else:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_book))))
        
        mock_db.query.side_effect = query_side_effect
        
        request = library_service_pb2.ApproveBookRequestReq(
            request_id=1,
            admin_id=1
        )
        
        response = self.service.ApproveBookRequest(request, None)
        
        self.assertFalse(response.success)
        self.assertEqual(response.message, "Book no longer available")

if __name__ == '__main__':
    unittest.main()