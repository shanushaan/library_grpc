import pytest
from unittest.mock import AsyncMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.test_helpers import (
    create_mock_grpc_client, create_mock_user, create_mock_book,
    create_mock_transaction, create_mock_request
)
from utils.mock_data import MOCK_USERS, MOCK_BOOKS, MOCK_TRANSACTIONS, MOCK_REQUESTS

class TestHelpers:
    """Test utility helper functions"""
    
    def test_create_mock_grpc_client(self):
        client = create_mock_grpc_client()
        assert isinstance(client, AsyncMock)
    
    def test_create_mock_user_default(self):
        user = create_mock_user()
        assert user.user_id == 1
        assert user.username == "testuser"
        assert user.role == "USER"
        assert user.email == "testuser@test.com"
        assert user.is_active == True
    
    def test_create_mock_user_custom(self):
        user = create_mock_user(user_id=5, username="admin", role="ADMIN")
        assert user.user_id == 5
        assert user.username == "admin"
        assert user.role == "ADMIN"
        assert user.email == "admin@test.com"
    
    def test_create_mock_book_default(self):
        book = create_mock_book()
        assert book.book_id == 1
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.available_copies == 5
    
    def test_create_mock_book_custom(self):
        book = create_mock_book(book_id=2, title="Custom Book", available_copies=0)
        assert book.book_id == 2
        assert book.title == "Custom Book"
        assert book.available_copies == 0
    
    def test_create_mock_transaction_default(self):
        transaction = create_mock_transaction()
        assert transaction.transaction_id == 1
        assert transaction.member_id == 1
        assert transaction.book_id == 1
        assert transaction.transaction_type == "ISSUE"
        assert transaction.status == "BORROWED"
    
    def test_create_mock_request_default(self):
        request = create_mock_request()
        assert request.request_id == 1
        assert request.user_id == 1
        assert request.book_id == 1
        assert request.request_type == "ISSUE"
        assert request.status == "PENDING"

class TestMockData:
    """Test mock data constants"""
    
    def test_mock_users_structure(self):
        assert len(MOCK_USERS) == 2
        assert MOCK_USERS[0]["username"] == "testuser"
        assert MOCK_USERS[1]["role"] == "ADMIN"
    
    def test_mock_books_structure(self):
        assert len(MOCK_BOOKS) == 2
        assert MOCK_BOOKS[0]["title"] == "Test Book 1"
        assert MOCK_BOOKS[1]["available_copies"] == 0
    
    def test_mock_transactions_structure(self):
        assert len(MOCK_TRANSACTIONS) == 1
        assert MOCK_TRANSACTIONS[0]["transaction_type"] == "ISSUE"
        assert MOCK_TRANSACTIONS[0]["status"] == "BORROWED"
    
    def test_mock_requests_structure(self):
        assert len(MOCK_REQUESTS) == 1
        assert MOCK_REQUESTS[0]["request_type"] == "ISSUE"
        assert MOCK_REQUESTS[0]["status"] == "PENDING"