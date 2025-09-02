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
```