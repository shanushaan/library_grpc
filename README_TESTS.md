# Unit Tests for Library Management System

## Overview
This project includes comprehensive unit tests for both the gRPC backend service and FastAPI gateway.

## Test Structure

### gRPC Service Tests (`grpc-server/tests/`)
- **test_library_service.py**: Tests core gRPC service functionality
  - `test_authenticate_user_success`: Validates successful user authentication
  - `test_get_books`: Tests book retrieval functionality

### API Gateway Tests (`api-gateway/tests/`)
- **test_gateway.py**: Tests FastAPI endpoints
  - `test_login_success`: Tests login endpoint with mocked gRPC calls
  - `test_search_books`: Tests book search API endpoint
  - `test_create_book_request`: Tests book request creation

## Running Tests

### Option 1: Docker-based Testing (Recommended)
```bash
# Test gRPC Service
docker-compose -f docker-compose.test.yml run --rm grpc-server-test

# Test API Gateway
docker-compose -f docker-compose.test.yml run --rm api-gateway-test
```

### Option 2: Local Testing Script
```bash
python run_tests.py
```

## Test Results
- ✅ **gRPC Service Tests**: 2/2 PASSED
- ✅ **API Gateway Tests**: 3/3 PASSED
- ✅ **Total Coverage**: 5/5 tests passing

## Test Features
- **Mocking**: Uses unittest.mock for database and gRPC client mocking
- **Isolation**: Tests run in isolated Docker containers
- **Dependencies**: All test dependencies included in requirements.txt
- **Coverage**: Tests cover authentication, book operations, and request handling

## Dependencies
- `unittest` (built-in Python testing framework)
- `pytest` and `pytest-mock` (for advanced testing features)
- `httpx` (for FastAPI testing client)
- Docker containers ensure consistent test environment