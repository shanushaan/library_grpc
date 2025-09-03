import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.book_service import BookService
import library_service_pb2

class TestBookService(unittest.TestCase):
    
    def setUp(self):
        self.book_service = BookService()
    
    @patch('services.book_service.db_pool')
    def test_get_books_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock book data
        mock_cursor.fetchall.return_value = [
            (1, 'Test Book', 'Test Author', 'Fiction', 2023, 5, False)
        ]
        
        # Create request
        request = library_service_pb2.GetBooksRequest(search_query='')
        
        # Test get books
        response = self.book_service.get_books(request, None)
        
        # Assertions
        self.assertEqual(len(response.books), 1)
        self.assertEqual(response.books[0].title, 'Test Book')
        self.assertEqual(response.books[0].author, 'Test Author')
    
    @patch('services.book_service.db_pool')
    def test_create_book_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock book creation
        mock_cursor.fetchone.return_value = (1,)
        
        # Create request
        request = library_service_pb2.CreateBookRequest(
            title='New Book',
            author='New Author',
            genre='Fiction',
            published_year=2024,
            available_copies=3
        )
        
        # Test create book
        response = self.book_service.create_book(request, None)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.book.title, 'New Book')
        self.assertEqual(response.message, 'Book created successfully')
    
    @patch('services.book_service.db_pool')
    def test_delete_book_success(self, mock_db_pool):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Mock successful deletion
        mock_cursor.rowcount = 1
        
        # Create request
        request = library_service_pb2.Book(book_id=1)
        
        # Test delete book
        response = self.book_service.delete_book(request, None)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.message, 'Book deleted successfully')

if __name__ == '__main__':
    unittest.main()