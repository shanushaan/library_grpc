# Library Management System - Setup Guide

## 📝 Prerequisites

### Required Software
1. **Docker Desktop** (Latest version)
   - Windows: https://docs.docker.com/desktop/windows/install/
   - macOS: https://docs.docker.com/desktop/mac/install/
   - Linux: https://docs.docker.com/engine/install/

2. **Git** (For cloning repository)
   - Download: https://git-scm.com/downloads

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB
- **Storage**: 2GB free space
- **Ports**: 3000, 8001, 50051, 5432 must be available

## 🚀 Quick Setup (5 Minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/shanushaan/library_grpc.git
cd library_grpc
```

### Step 2: Start Services
```bash
# Recommended: Node.js API Gateway
docker-compose --profile node up -d

# Alternative: Python FastAPI Gateway
docker-compose --profile python up -d
```

### Step 3: Wait for Services (30-60 seconds)
```bash
# Check status
docker-compose ps

# Wait for all services to show "Up" status
```

### Step 4: Access Application
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8001

### Step 5: Login
- **Admin**: `admin` / `admin123`
- **User**: `logan_baker` / `user123` or `john_user` / `user123`

## 🔧 Detailed Setup Instructions

### 1. Environment Preparation

**Check Docker Installation:**
```bash
docker --version
docker-compose --version
```

**Check Port Availability:**
```bash
# Windows
netstat -an | findstr ":3000 :8001 :50051 :5432"

# Linux/macOS
netstat -an | grep -E ":3000|:8001|:50051|:5432"
```

### 2. Repository Setup

**Clone and Navigate:**
```bash
git clone https://github.com/shanushaan/library_grpc.git
cd library_grpc
ls -la  # Verify files are present
```

**Verify Project Structure:**
```
library_grpc/
├── api-gateway/          # Python FastAPI gateway
├── api-gateway-node/     # Node.js Express gateway
├── frontend/             # React application
├── grpc-server/          # gRPC backend service
├── db-init/              # Database initialization
├── proto/                # Protocol buffer definitions
├── shared/               # Common models
└── docker-compose.yml    # Service orchestration
```

### 3. Service Deployment

**Option A: Node.js Gateway (Recommended)**
```bash
# Start with Node.js gateway
docker-compose --profile node up -d

# Services started:
# - PostgreSQL Database (port 5432)
# - gRPC Server (port 50051)
# - Node.js API Gateway (port 8001)
# - React Frontend (port 3000)
```

**Option B: Python FastAPI Gateway**
```bash
# Start with Python gateway
docker-compose --profile python up -d

# Services started:
# - PostgreSQL Database (port 5432)
# - gRPC Server (port 50051)
# - Python API Gateway (port 8001)
# - React Frontend (port 3000)
```

### 4. Service Verification

**Check Container Status:**
```bash
docker-compose ps

# Expected output:
# NAME                                    STATUS
# library_grpc-frontend-1                 Up
# library_grpc-postgres-1                 Up (healthy)
# library_grpc-grpc-server-1              Up
# library_grpc-api-gateway-node-1         Up
```

**Test API Gateway:**
```bash
curl http://localhost:8001/
# Expected: {"message":"Library API Gateway..."}
```

**Test Frontend:**
```bash
curl http://localhost:3000/
# Expected: HTML content
```

### 5. Database Verification

**Check Database Connection:**
```bash
docker exec library_grpc-postgres-1 psql -U postgres -d library_db -c "SELECT COUNT(*) FROM users;"
# Expected: 30 users

docker exec library_grpc-postgres-1 psql -U postgres -d library_db -c "SELECT COUNT(*) FROM books;"
# Expected: 104 books

docker exec library_grpc-postgres-1 psql -U postgres -d library_db -c "SELECT COUNT(*) FROM transactions;"
# Expected: 100 transactions
```

## 🔍 Troubleshooting

### Common Issues

**1. Port Conflicts**
```bash
# If ports are in use, modify docker-compose.yml:
ports:
  - "3001:3000"  # Change frontend port
  - "8002:8001"  # Change API gateway port
```

**2. Services Not Starting**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose --profile node up -d
```

**3. Database Issues**
```bash
# Reset database completely
docker-compose down -v
docker-compose --profile node up -d
```

**4. Permission Issues (Linux/macOS)**
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
# Logout and login again
```

**5. Memory Issues**
```bash
# Increase Docker memory limit in Docker Desktop settings
# Minimum: 4GB, Recommended: 8GB
```

### Service-Specific Troubleshooting

**Frontend Issues:**
```bash
# Check frontend logs
docker logs library_grpc-frontend-1

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

**API Gateway Issues:**
```bash
# Check gateway logs
docker logs library_grpc-api-gateway-node-1

# Test gateway directly
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Database Issues:**
```bash
# Check database logs
docker logs library_grpc-postgres-1

# Connect to database
docker exec -it library_grpc-postgres-1 psql -U postgres -d library_db
```

## 🔄 System Rebuild (Clean Environment)

### Complete System Reset
```bash
# 1. Stop all services
docker-compose down -v

# 2. Remove all containers and images (optional)
docker system prune -a

# 3. Rebuild everything
docker-compose build

# 4. Start fresh
docker-compose --profile node up -d

# 5. Verify deployment
docker-compose ps
```

### Switching Between Gateways
```bash
# Switch from Node.js to Python
docker-compose down
docker-compose --profile python up -d

# Switch from Python to Node.js
docker-compose down
docker-compose --profile node up -d
```

## 📊 System Monitoring

### Health Checks
```bash
# Check all services
docker-compose ps

# Check specific service health
docker inspect library_grpc-postgres-1 | grep Health

# Monitor logs in real-time
docker-compose logs -f
```

### Performance Monitoring
```bash
# Check resource usage
docker stats

# Check disk usage
docker system df
```

## 📝 Default Data

### Pre-loaded Users (30 total)
- **Admins**: admin, librarian, manager
- **Users**: logan_baker, john_user, jane_smith, mike_brown, + 23 more
- **WebSocket**: Real-time notifications for user ID 32 (logan_baker)

### Pre-loaded Books (104 unique)
- **Genres**: Fiction, Science Fiction, Fantasy, Mystery, Romance, Young Adult, Non-Fiction, Biography, History, Self-Help, Classic Literature
- **Inventory**: 1-10 copies per book

### Pre-loaded Transactions (100 total)
- **Active**: 15 current borrowings
- **Overdue**: 8 books with fines
- **Returned**: 77 completed transactions
- **Timeline**: July 2023 - February 2024

## 🔒 Security Notes

### Default Passwords
- Change default passwords in production
- Passwords are SHA-256 hashed in database
- Session-based authentication

### Network Security
- Services communicate via Docker network
- Only necessary ports exposed to host
- CORS configured for frontend access

## 🧪 Testing

### Python API Gateway Testing

**Prerequisites:**
```bash
# Navigate to Python gateway directory
cd api-gateway

# Install test dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov httpx
```

**Run Organized Test Suite:**
```bash
# Run all tests with coverage
python run_organized_tests.py

# Expected output:
# Core Tests: PASSED (9 tests)
# Route Tests: PASSED (34 tests)
# Service Tests: PASSED (20 tests)
# Integration Tests: PASSED (1 test)
# Unit Tests: PASSED (36 tests)
```

**Run Specific Test Categories:**
```bash
# Core validation tests
pytest tests/core/ -v

# API route tests
pytest tests/routes/ -v

# Business logic tests
pytest tests/services/ -v

# Component unit tests
pytest tests/unit/ -v

# End-to-end integration tests
pytest tests/integration/ -v
```

**Test Coverage Report:**
```bash
# Generate HTML coverage report
pytest --cov=routes --cov=services --cov=core --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

**Test Categories:**
- **Core Tests (9)**: Input validation, utility functions
- **Route Tests (34)**: API endpoints, authentication, CRUD operations
- **Service Tests (20)**: Business logic, gRPC integration, error handling
- **Integration Tests (1)**: End-to-end user workflows
- **Unit Tests (36)**: Individual components, mocking, edge cases

**Admin Restriction Testing:**
```bash
# Test admin cannot request book issues
pytest tests/services/test_admin_restrictions.py -v

# Expected: 3 tests pass
# - Admin ISSUE blocked (403 Forbidden)
# - Admin RETURN allowed (Success)
# - Regular user ISSUE allowed (Success)
```

### Node.js API Gateway Testing

**Prerequisites:**
```bash
# Navigate to Node.js gateway directory
cd api-gateway-node

# Install test dependencies
npm install --save-dev jest supertest
```

**Run Tests:**
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage
```

### Frontend Testing

**Prerequisites:**
```bash
# Navigate to frontend directory
cd frontend

# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

**Run Tests:**
```bash
# Run component tests
npm test

# Run with coverage
npm run test:coverage
```

### Integration Testing (Full System)

**API Integration Tests:**
```bash
# From project root
python run_api_tests.py

# Tests all API endpoints with real backend
```

**Manual Testing Scenarios:**
```bash
# 1. User Authentication
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. Book Search
curl "http://localhost:8001/api/v1/user/books/search?q=python"

# 3. Admin Restriction (should fail)
curl -X POST http://localhost:8001/api/v1/user/book-request \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"request_type":"ISSUE","user_id":2}'
```

### Failure Scenario Testing

**Test Frontend Resilience:**
```bash
# 1. Stop API Gateway
docker stop library_grpc-api-gateway-python-1

# 2. Test frontend at http://localhost:3000
# Expected: Graceful error messages, no crashes

# 3. Restart API Gateway
docker start library_grpc-api-gateway-python-1

# 4. Verify recovery
# Expected: Frontend reconnects automatically
```

**Database Failure Testing:**
```bash
# 1. Stop database
docker stop library_grpc-postgres-1

# 2. Test API endpoints
# Expected: 500 errors with proper messages

# 3. Restart database
docker start library_grpc-postgres-1
```

### Performance Testing

**Load Testing:**
```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Linux
brew install httpie                 # macOS

# Test API performance
ab -n 1000 -c 10 http://localhost:8001/api/v1/user/books/search?q=test
```

**Memory Usage:**
```bash
# Monitor container resources
docker stats

# Expected: <500MB per container
```

### Test Data Management

**Reset Test Data:**
```bash
# Reset database to clean state
docker-compose down -v
docker-compose --profile python up -d

# Wait for initialization (30-60 seconds)
docker-compose logs postgres | grep "ready to accept connections"
```

**Custom Test Data:**
```bash
# Add test users/books via API
curl -X POST http://localhost:8001/api/v1/admin/users \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","role":"USER"}'
```

## 📞 Support

### Getting Help
1. Check logs: `docker-compose logs`
2. Verify prerequisites are met
3. Ensure ports are available
4. Try complete system reset
5. Check GitHub issues: https://github.com/shanushaan/library_grpc/issues

### Useful Commands Reference
```bash
# Start system
docker-compose --profile node up -d

# Stop system
docker-compose down

# Reset database
docker-compose down -v && docker-compose --profile node up -d

# View logs
docker-compose logs [service-name]

# Check status
docker-compose ps

# Rebuild
docker-compose build && docker-compose --profile node up -d

# Run Python tests
cd api-gateway && python run_organized_tests.py

# Test admin restrictions
cd api-gateway && pytest tests/services/test_admin_restrictions.py -v
```