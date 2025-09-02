from unittest.mock import AsyncMock

def create_mock_grpc_client():
    """Create a mock gRPC client for testing"""
    return AsyncMock()

def create_mock_user(user_id=1, username="testuser", role="USER"):
    """Create a mock user object for testing"""
    mock_user = AsyncMock()
    mock_user.user_id = user_id
    mock_user.username = username
    mock_user.email = f"{username}@test.com"
    mock_user.role = role
    mock_user.is_active = True
    return mock_user

def create_mock_book(book_id=1, title="Test Book", available_copies=5):
    """Create a mock book object for testing"""
    mock_book = AsyncMock()
    mock_book.book_id = book_id
    mock_book.title = title
    mock_book.author = "Test Author"
    mock_book.genre = "Fiction"
    mock_book.published_year = 2023
    mock_book.available_copies = available_copies
    return mock_book

def create_mock_transaction(transaction_id=1, user_id=1, book_id=1):
    """Create a mock transaction object for testing"""
    mock_transaction = AsyncMock()
    mock_transaction.transaction_id = transaction_id
    mock_transaction.member_id = user_id
    mock_transaction.book_id = book_id
    mock_transaction.transaction_type = "ISSUE"
    mock_transaction.status = "BORROWED"
    mock_transaction.fine_amount = 0.0
    return mock_transaction

def create_mock_request(request_id=1, user_id=1, book_id=1, request_type="ISSUE"):
    """Create a mock book request object for testing"""
    mock_request = AsyncMock()
    mock_request.request_id = request_id
    mock_request.user_id = user_id
    mock_request.book_id = book_id
    mock_request.request_type = request_type
    mock_request.status = "PENDING"
    mock_request.notes = "Test request"
    mock_request.transaction_id = 0
    return mock_request