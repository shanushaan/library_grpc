import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.book_service import BookService
from services.request_service import RequestService

pytestmark = pytest.mark.asyncio

class TestBookService:
    """Test book service business logic"""
    
    async def test_search_books_success(self):
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
        
        book_service = BookService(mock_client)
        result = await book_service.search_books("test")
        
        assert len(result) == 1
        assert result[0]["title"] == "Test Book"
        assert result[0]["can_request"] == True
    
    async def test_search_books_empty_result(self):
        mock_client = AsyncMock()
        mock_client.GetBooks.return_value.books = []
        
        book_service = BookService(mock_client)
        result = await book_service.search_books("nonexistent")
        
        assert len(result) == 0
    
    async def test_issue_book_success(self):
        mock_client = AsyncMock()
        
        # Mock book availability check
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
        
        book_service = BookService(mock_client)
        result = await book_service.issue_book(1, 1)
        
        assert result["transaction_id"] == 1
        assert result["message"] == "Book issued"
    
    async def test_issue_book_not_found(self):
        mock_client = AsyncMock()
        mock_client.GetBooks.return_value.books = []
        
        book_service = BookService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await book_service.issue_book(999, 1)
        
        assert exc_info.value.status_code == 404
        assert "Book not found" in str(exc_info.value.detail)
    
    async def test_issue_book_no_copies(self):
        mock_client = AsyncMock()
        
        # Mock book with no copies
        mock_book = AsyncMock()
        mock_book.book_id = 1
        mock_book.available_copies = 0
        mock_client.GetBooks.return_value.books = [mock_book]
        
        book_service = BookService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await book_service.issue_book(1, 1)
        
        assert exc_info.value.status_code == 400
        assert "No copies available" in str(exc_info.value.detail)
    
    async def test_return_book_success(self):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.transaction.transaction_id = 1
        mock_response.transaction.fine_amount = 5.0
        mock_response.message = "Book returned"
        
        mock_client.ReturnBook.return_value = mock_response
        
        book_service = BookService(mock_client)
        result = await book_service.return_book(1)
        
        assert result["transaction_id"] == 1
        assert result["fine_amount"] == 5.0
        assert result["message"] == "Book returned"
    
    async def test_return_book_failure(self):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = False
        mock_response.message = "Transaction not found"
        
        mock_client.ReturnBook.return_value = mock_response
        
        book_service = BookService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await book_service.return_book(999)
        
        assert exc_info.value.status_code == 400
        assert "Transaction not found" in str(exc_info.value.detail)

class TestRequestService:
    """Test request service business logic"""
    
    async def test_create_book_request_success(self):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.request.request_id = 1
        mock_response.request.status = "PENDING"
        mock_response.message = "Request created"
        
        mock_client.CreateUserBookRequest.return_value = mock_response
        
        request_service = RequestService(mock_client)
        result = await request_service.create_book_request(1, 1, "ISSUE", None, "Test notes")
        
        assert result["request_id"] == 1
        assert result["status"] == "PENDING"
        assert result["message"] == "Request created"
    
    async def test_create_book_request_failure(self):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.success = False
        mock_response.message = "Request failed"
        
        mock_client.CreateUserBookRequest.return_value = mock_response
        
        request_service = RequestService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await request_service.create_book_request(1, 1, "ISSUE", None, "Test notes")
        
        assert exc_info.value.status_code == 400
        assert "Request failed" in str(exc_info.value.detail)
    
    async def test_get_admin_book_requests_success(self):
        mock_client = AsyncMock()
        
        # Mock request
        mock_request = AsyncMock()
        mock_request.request_id = 1
        mock_request.user_id = 1
        mock_request.book_id = 1
        mock_request.request_type = "ISSUE"
        mock_request.status = "PENDING"
        mock_request.notes = "Test request"
        mock_request.request_date = "2023-01-01"
        
        # Mock book
        mock_book = AsyncMock()
        mock_book.book_id = 1
        mock_book.title = "Test Book"
        mock_book.author = "Test Author"
        mock_book.available_copies = 5
        
        # Mock user
        mock_user = AsyncMock()
        mock_user.user_id = 1
        mock_user.username = "testuser"
        
        mock_client.GetBookRequests.return_value.requests = [mock_request]
        mock_client.GetBooks.return_value.books = [mock_book]
        mock_client.GetUsers.return_value.users = [mock_user]
        
        request_service = RequestService(mock_client)
        result = await request_service.get_admin_book_requests()
        
        assert len(result) == 1
        assert result[0]["request_id"] == 1
        assert result[0]["book_title"] == "Test Book"
        assert result[0]["user_name"] == "testuser"
    
    async def test_get_admin_book_requests_missing_book(self):
        mock_client = AsyncMock()
        
        # Mock request with book_id that doesn't exist
        mock_request = AsyncMock()
        mock_request.request_id = 1
        mock_request.user_id = 1
        mock_request.book_id = 999
        mock_request.request_type = "ISSUE"
        mock_request.status = "PENDING"
        mock_request.notes = "Test request"
        mock_request.request_date = "2023-01-01"
        
        mock_client.GetBookRequests.return_value.requests = [mock_request]
        mock_client.GetBooks.return_value.books = []  # No books
        mock_client.GetUsers.return_value.users = []
        
        request_service = RequestService(mock_client)
        result = await request_service.get_admin_book_requests()
        
        assert len(result) == 1
        assert result[0]["book_title"] == "Unknown"
        assert result[0]["book_author"] == "Unknown"
    
    async def test_get_user_book_requests_success(self):
        mock_client = AsyncMock()
        
        # Mock request
        mock_request = AsyncMock()
        mock_request.request_id = 1
        mock_request.user_id = 1
        mock_request.book_id = 1
        mock_request.request_type = "ISSUE"
        mock_request.status = "PENDING"
        mock_request.notes = "Test request"
        mock_request.request_date = "2023-01-01"
        mock_request.transaction_id = 0
        
        # Mock book
        mock_book = AsyncMock()
        mock_book.book_id = 1
        mock_book.title = "Test Book"
        mock_book.author = "Test Author"
        
        mock_client.GetBookRequests.return_value.requests = [mock_request]
        mock_client.GetBooks.return_value.books = [mock_book]
        mock_client.GetTransactions.return_value.transactions = []
        
        request_service = RequestService(mock_client)
        result = await request_service.get_user_book_requests(1)
        
        assert len(result) == 1
        assert result[0]["request_id"] == 1
        assert result[0]["book_title"] == "Test Book"
    
    async def test_get_user_book_requests_return_type(self):
        mock_client = AsyncMock()
        
        # Mock return request with transaction
        mock_request = AsyncMock()
        mock_request.request_id = 1
        mock_request.user_id = 1
        mock_request.book_id = 0
        mock_request.request_type = "RETURN"
        mock_request.status = "PENDING"
        mock_request.notes = "Return request"
        mock_request.request_date = "2023-01-01"
        mock_request.transaction_id = 1
        
        # Mock transaction
        mock_transaction = AsyncMock()
        mock_transaction.transaction_id = 1
        mock_transaction.book_id = 1
        
        # Mock book
        mock_book = AsyncMock()
        mock_book.book_id = 1
        mock_book.title = "Test Book"
        mock_book.author = "Test Author"
        
        mock_client.GetBookRequests.return_value.requests = [mock_request]
        mock_client.GetBooks.return_value.books = [mock_book]
        mock_client.GetTransactions.return_value.transactions = [mock_transaction]
        
        request_service = RequestService(mock_client)
        result = await request_service.get_user_book_requests(1)
        
        assert len(result) == 1
        assert result[0]["request_type"] == "RETURN"
        assert result[0]["book_title"] == "Test Book"