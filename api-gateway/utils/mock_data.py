"""Mock data for testing purposes"""

MOCK_USERS = [
    {
        "user_id": 1,
        "username": "testuser",
        "email": "testuser@test.com",
        "role": "USER",
        "is_active": True
    },
    {
        "user_id": 2,
        "username": "admin",
        "email": "admin@test.com", 
        "role": "ADMIN",
        "is_active": True
    }
]

MOCK_BOOKS = [
    {
        "book_id": 1,
        "title": "Test Book 1",
        "author": "Test Author 1",
        "genre": "Fiction",
        "published_year": 2023,
        "available_copies": 5
    },
    {
        "book_id": 2,
        "title": "Test Book 2", 
        "author": "Test Author 2",
        "genre": "Non-Fiction",
        "published_year": 2022,
        "available_copies": 0
    }
]

MOCK_TRANSACTIONS = [
    {
        "transaction_id": 1,
        "member_id": 1,
        "book_id": 1,
        "transaction_type": "ISSUE",
        "status": "BORROWED",
        "fine_amount": 0.0
    }
]

MOCK_REQUESTS = [
    {
        "request_id": 1,
        "user_id": 1,
        "book_id": 1,
        "request_type": "ISSUE",
        "status": "PENDING",
        "notes": "Test request",
        "transaction_id": 0
    }
]