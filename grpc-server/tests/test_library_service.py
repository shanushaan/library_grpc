import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.library_service import LibraryServiceImpl
import library_service_pb2

class TestLibraryService(unittest.TestCase):
    
    def setUp(self):
        self.service = LibraryServiceImpl()
        
    @patch('services.library_service.SessionLocal')
    def test_authenticate_user_success(self, mock_session):
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        mock_user = Mock()
        mock_user.user_id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@test.com"
        mock_user.role = "USER"
        mock_user.is_active = True
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        request = library_service_pb2.AuthRequest(
            username="testuser",
            password="password123"
        )
        
        response = self.service.AuthenticateUser(request, None)
        
        self.assertTrue(response.success)
        self.assertEqual(response.user.username, "testuser")
        
    @patch('services.library_service.SessionLocal')
    def test_get_books(self, mock_session):
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        mock_book = Mock()
        mock_book.book_id = 1
        mock_book.title = "Test Book"
        mock_book.author = "Test Author"
        mock_book.genre = "Fiction"
        mock_book.published_year = 2023
        mock_book.available_copies = 5
        
        mock_db.query.return_value.all.return_value = [mock_book]
        
        request = library_service_pb2.GetBooksRequest(search_query="")
        response = self.service.GetBooks(request, None)
        
        self.assertEqual(len(response.books), 1)
        self.assertEqual(response.books[0].title, "Test Book")
        
    @patch('services.library_service.SessionLocal')
    def test_authenticate_user_invalid_credentials(self, mock_session):
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        request = library_service_pb2.AuthRequest(
            username="invalid",
            password="wrong"
        )
        
        response = self.service.AuthenticateUser(request, None)
        
        self.assertFalse(response.success)
        self.assertEqual(response.message, "Invalid credentials")
        
    @patch('services.library_service.SessionLocal')
    def test_issue_book_not_available(self, mock_session):
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        mock_book = Mock()
        mock_book.available_copies = 0
        mock_db.query.return_value.filter.return_value.first.return_value = mock_book
        
        request = library_service_pb2.IssueBookRequest(
            book_id=1,
            member_id=1,
            admin_id=1
        )
        
        response = self.service.IssueBook(request, None)
        
        self.assertFalse(response.success)
        self.assertEqual(response.message, "Book not available")
        
    @patch('services.library_service.SessionLocal')
    def test_issue_book_user_not_found(self, mock_session):
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        mock_book = Mock()
        mock_book.available_copies = 5
        
        def side_effect(model):
            if model == Mock:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_book))))
            return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
        
        mock_db.query.side_effect = side_effect
        
        request = library_service_pb2.IssueBookRequest(
            book_id=1,
            member_id=999,
            admin_id=1
        )
        
        response = self.service.IssueBook(request, None)
        
        self.assertFalse(response.success)
        self.assertEqual(response.message, "User not found")
        
    @patch('services.library_service.SessionLocal')
    def test_approve_request_not_found(self, mock_session):
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        request = library_service_pb2.ApproveBookRequestReq(
            request_id=999,
            admin_id=1
        )
        
        response = self.service.ApproveBookRequest(request, None)
        
        self.assertFalse(response.success)
        self.assertEqual(response.message, "Request not found or already processed")
        
    @patch('services.library_service.SessionLocal')
    def test_reject_request_not_found(self, mock_session):
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        request = library_service_pb2.RejectBookRequestReq(
            request_id=999,
            admin_id=1
        )
        
        response = self.service.RejectBookRequest(request, None)
        
        self.assertFalse(response.success)
        self.assertEqual(response.message, "Request not found or already processed")

if __name__ == '__main__':
    unittest.main()