import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock
import grpc
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.auth_service import AuthService
from services.book_service import BookService

pytestmark = pytest.mark.asyncio

class TestErrorHandling:
    """Test error handling across services"""
    
    async def test_auth_service_grpc_unavailable(self):
        mock_client = AsyncMock()
        mock_client.AuthenticateUser.side_effect = grpc.RpcError("Service unavailable")
        
        auth_service = AuthService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user("user", "pass")
        
        assert exc_info.value.status_code == 500
        assert "Authentication service unavailable" in str(exc_info.value.detail)
    
    async def test_book_service_grpc_timeout(self):
        mock_client = AsyncMock()
        mock_client.GetBooks.side_effect = grpc.RpcError("Timeout")
        
        book_service = BookService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await book_service.search_books("test")
        
        assert exc_info.value.status_code == 500
        assert "Book search service unavailable" in str(exc_info.value.detail)
    
    async def test_book_service_unexpected_error(self):
        mock_client = AsyncMock()
        mock_client.GetBooks.side_effect = Exception("Unexpected error")
        
        book_service = BookService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await book_service.search_books("test")
        
        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value.detail)
    
    async def test_book_issue_validation_error(self):
        mock_client = AsyncMock()
        mock_client.GetBooks.return_value.books = []  # No books found
        
        book_service = BookService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await book_service.issue_book(999, 1)
        
        assert exc_info.value.status_code == 404
        assert "Book not found" in str(exc_info.value.detail)
    
    async def test_book_issue_business_rule_error(self):
        mock_client = AsyncMock()
        
        # Mock book with no copies
        mock_book = type('MockBook', (), {
            'book_id': 1,
            'available_copies': 0
        })()
        mock_client.GetBooks.return_value.books = [mock_book]
        
        book_service = BookService(mock_client)
        
        with pytest.raises(HTTPException) as exc_info:
            await book_service.issue_book(1, 1)
        
        assert exc_info.value.status_code == 400
        assert "No copies available" in str(exc_info.value.detail)