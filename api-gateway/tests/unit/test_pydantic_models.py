import pytest
from pydantic import ValidationError
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from routes.auth import LoginRequest
from routes.books import IssueBookRequest, ReturnBookRequest
from routes.requests import UserBookRequest

class TestPydanticModels:
    """Test Pydantic model validation"""
    
    def test_login_request_valid(self):
        request = LoginRequest(username="testuser", password="password123")
        assert request.username == "testuser"
        assert request.password == "password123"
    
    def test_login_request_invalid_username(self):
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(username="ab", password="password123")
        assert "at least 3 characters" in str(exc_info.value)
    
    def test_login_request_invalid_password(self):
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(username="testuser", password="123")
        assert "at least 6 characters" in str(exc_info.value)
    
    def test_issue_book_request_valid(self):
        request = IssueBookRequest(book_id=1, user_id=1)
        assert request.book_id == 1
        assert request.user_id == 1
    
    def test_issue_book_request_invalid_ids(self):
        with pytest.raises(ValidationError) as exc_info:
            IssueBookRequest(book_id=0, user_id=1)
        assert "greater than 0" in str(exc_info.value)
    
    def test_return_book_request_valid(self):
        request = ReturnBookRequest(transaction_id=1)
        assert request.transaction_id == 1
    
    def test_user_book_request_valid(self):
        request = UserBookRequest(
            book_id=1, request_type="ISSUE", user_id=1, notes="Test"
        )
        assert request.book_id == 1
        assert request.request_type == "ISSUE"
        assert request.user_id == 1
        assert request.notes == "Test"
    
    def test_user_book_request_invalid_type(self):
        with pytest.raises(ValidationError) as exc_info:
            UserBookRequest(book_id=1, request_type="INVALID", user_id=1)
        assert "ISSUE, RETURN" in str(exc_info.value)