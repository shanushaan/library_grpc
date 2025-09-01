# Library Management System

A comprehensive microservices-based library management system built with  gRPC backend, async FastAPI OR NODE gateway, React frontend, and PostgreSQL database with advanced features like pagination, structured logging, and performance optimization.

## 🚀 Key Features

### 📚 Book Management
- **Complete Book Catalog**: 104 unique books across 11 genres (Fiction, Science Fiction, Fantasy, Mystery, etc.)
- **Advanced Search & Filtering**: Search by title, author, or genre with real-time results
- **Inventory Management**: Automatic available copies tracking
- **Tabular Display**: Professional data tables with sorting and filtering

### 👥 User Management & Authentication
- **Role-Based Access Control**: Admin and User roles with different permissions
- **Secure Authentication**: SHA-256 password hashing with session management
- **User Profiles**: Complete user information with activity tracking
- **30 Pre-loaded Users**: 3 admins + 27 regular users for testing

### 📋 Request & Transaction System
- **Book Request Workflow**: Users request books → Admin approval → Automatic inventory update
- **Issue/Return Management**: Complete transaction lifecycle tracking
- **Due Date Management**: 30-day borrowing period with automatic due date calculation
- **Fine System**: ₹10/day fine for overdue books with automatic calculation
- **3-Book Limit**: Users can borrow maximum 3 books simultaneously

### 📊 Dashboard & Analytics
- **User Dashboard**: Personal statistics (books taken, currently borrowed, overdue, fines)
- **Admin Dashboard**: System-wide statistics and management tools
- **Real-time Data**: Live updates of book availability and user statistics
- **Transaction History**: Complete audit trail with pagination

### 🔧 Advanced Technical Features
- **Async Performance**: FastAPI with async/await and concurrent processing
- **Structured JSON Logging**: Comprehensive logging for monitoring and debugging
- **Pagination**: Efficient data loading with 20 items per page (admin transactions)
- **Microservices Architecture**: Scalable gRPC backend with REST API gateway
- **Docker Orchestration**: Complete containerized deployment
- **Database Optimization**: Clean data structure with proper relationships and indexes

## Architecture

- **Backend**: gRPC service (Python)
- **API Gateway**: FastAPI (Python) or Node ( JS)
- **Frontend**: React.js
- **Database**: PostgreSQL
- **Orchestration**: Docker Compose

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop**: Latest version with Docker Compose
- **Git**: For cloning the repository
- **Ports Available**: 3000, 8001, 50051, 5432

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/shanushaan/library_grpc.git
cd library_grpc
```

2. **Choose API Gateway (Node.js recommended):**
```bash
# Option A: Node.js Gateway (Recommended)
docker-compose --profile node up -d

# Option B: Python FastAPI Gateway
docker-compose --profile python up -d
```

3. **Wait for services to start** (30-60 seconds)
   - Monitor with: `docker-compose ps`
   - All services should show "Up" status

4. **Access the application:**
   - **Frontend**: http://localhost:3000
   - **API Gateway**: http://localhost:8001
   - **API Documentation**: http://localhost:8001/docs (Python only)

### 🔑 Default Login Credentials

**Administrator Accounts:**
- Username: `admin` / Password: `admin123`
- Username: `librarian` / Password: `lib123`
- Username: `manager` / Password: `mgr123`

**Regular User Accounts:**
- Username: `john_user` / Password: `user123`
- Username: `jane_smith` / Password: `jane123`
- Username: `mike_brown` / Password: `mike123`
- *...and 24 more users for comprehensive testing*

**Quick Test Scenarios:**
1. **Admin Login**: Use `admin/admin123` to access full system management
2. **User Login**: Use `john_user/user123` to test user features
3. **Book Search**: Search for "Harry Potter" or "Science Fiction"
4. **Request Flow**: Request a book as user → Approve as admin
5. **Dashboard**: View statistics and transaction history

## Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React application |
| API Gateway | 8001 | FastAPI REST API |
| gRPC Server | 50051 | Core business logic |
| PostgreSQL | 5432 | Database |

## 📊 Database & Sample Data

The system comes with comprehensive pre-populated data for immediate testing:

### Books (104 unique titles)
- **Fiction**: Classic literature (Great Gatsby, Pride and Prejudice, etc.)
- **Science Fiction**: Modern sci-fi (Dune, 1984, Foundation, etc.)
- **Fantasy**: Popular fantasy (Harry Potter series, Lord of the Rings, etc.)
- **Mystery/Thriller**: Crime novels (Gone Girl, Da Vinci Code, etc.)
- **Romance**: Love stories (The Notebook, Fault in Our Stars, etc.)
- **Young Adult**: Teen fiction (Hunger Games, Divergent, etc.)
- **Non-Fiction**: Educational content (Sapiens, Educated, etc.)
- **Biography**: Life stories (Becoming, John Adams, etc.)
- **History**: Historical accounts (Band of Brothers, Diary of Anne Frank, etc.)
- **Self-Help**: Personal development (Atomic Habits, 7 Habits, etc.)
- **Classic Literature**: Timeless works (War and Peace, Don Quixote, etc.)

### Users (30 total)
- **3 Administrators**: Full system access
- **27 Regular Users**: Standard borrowing privileges
- **Realistic Data**: Proper names, emails, and activity history

### Transactions (100 records)
- **23 Active Borrowings**: 15 current + 8 overdue books
- **77 Returned Books**: Complete transaction history
- **Overdue Fines**: ₹10-₹320 accumulated fines
- **Realistic Timeline**: 6+ months of library activity (July 2023 - February 2024)
- **Transaction Types**: Borrow/Return with proper due dates and fine calculations

## Development

### Project Structure
```
library-grpc-service/
├── grpc-server/          # gRPC backend service
├── api-gateway/          # FastAPI REST gateway
├── frontend/             # React application
├── shared/               # Common models & database config
├── proto/                # Protocol buffer definitions
├── db-init/              # Database initialization scripts
└── docker-compose.yml    # Service orchestration
```

### 🔧 Development Commands

**Stop Services:**
```bash
docker-compose down
```

**View Logs:**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs frontend
docker-compose logs api-gateway-node
docker-compose logs grpc-server
```

**Rebuild Services:**
```bash
# Rebuild all
docker-compose build

# Rebuild and restart
docker-compose up --build -d
```

**Reset Database:**
```bash
# Remove volumes and restart
docker-compose down -v
docker-compose --profile node up -d
```

**Switch API Gateway:**
```bash
# Switch to Python gateway
docker-compose down
docker-compose --profile python up -d

# Switch to Node.js gateway
docker-compose down
docker-compose --profile node up -d
```

## 🔌 API Endpoints

### Authentication
- `POST /login` - User authentication with role-based access

### Book Management
- `GET /user/books/search?q={query}` - Search books by title, author, or genre
- `GET /admin/books?q={query}` - Admin book catalog management

### User Operations
- `GET /user/{user_id}/stats` - Dashboard statistics (borrowed, overdue, fines)
- `GET /user/{user_id}/transactions?status={status}` - Transaction history
- `GET /user/{user_id}/book-requests` - User's book requests
- `POST /user/book-request` - Create new book request (issue/return)

### Admin Operations
- `GET /admin/users` - User management interface
- `GET /admin/transactions?page={page}&limit={limit}&status={status}` - **Paginated** transaction history
- `GET /admin/book-requests` - Pending book requests management
- `POST /admin/book-requests/{id}/approve` - Approve book requests
- `POST /admin/book-requests/{id}/reject` - Reject book requests with notes
- `POST /admin/issue-book` - Direct book issuance
- `POST /admin/return-book` - Direct book return

### System Features
- **Pagination**: Efficient data loading (20 items per page)
- **Filtering**: Status-based filtering for transactions and requests
- **Search**: Real-time search across multiple fields
- **Concurrent Processing**: Async API calls for better performance

## 🛠️ Technology Stack

### Backend Services
- **gRPC Server**: Python 3.10, gRPC, SQLAlchemy ORM
- **API Gateway**: FastAPI (async), Pydantic validation, CORS middleware
- **Database**: PostgreSQL 13 with comprehensive sample data
- **Authentication**: SHA-256 hashing, role-based access control

### Frontend
- **Framework**: React 18 with modern hooks
- **HTTP Client**: Axios for API communication
- **Icons**: Lucide React icon library
- **Styling**: Custom CSS with responsive design
- **Components**: Modular component architecture

### DevOps & Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose with health checks
- **Logging**: Structured JSON logging across all services
- **Development**: Hot reload for both frontend and backend

### Performance Features
- **Async Processing**: FastAPI with asyncio for concurrent operations
- **Connection Pooling**: Efficient database connections
- **Pagination**: Memory-efficient data loading
- **Caching**: Optimized data retrieval patterns

## 🏗️ System Architecture

```
┌─────────────────┐    ┌────────────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI/Node Gateway │    │   gRPC Server   │
│   (Port 3000)    │◄──►│   (Port 8001)        │◄──►(Port 50051)  │
└─────────────────┘    └────────────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   CORS & Auth   │    │  Business Logic │
                       │   Validation    │    │  Data Processing│
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │  PostgreSQL DB  │
                                              │   (Port 5432)   │
                                              └─────────────────┘
```

## 📈 Performance Optimizations

- **Async API Gateway**: All endpoints use async/await for better concurrency
- **Concurrent gRPC Calls**: Multiple API calls processed simultaneously
- **Efficient Pagination**: Large datasets loaded in chunks
- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: Reused database connections
- **Structured Logging**: JSON logs for better monitoring and debugging

## 🔒 Security Features

- **Password Hashing**: SHA-256 encryption for user passwords
- **Role-Based Access**: Admin and User roles with different permissions
- **Input Validation**: Pydantic models for API request validation
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

## 📝 Business Rules

- **Borrowing Limit**: Users can borrow maximum 3 books simultaneously
- **Loan Period**: 30-day borrowing period for all books
- **Fine System**: ₹10 per day for overdue books
- **Request Workflow**: User requests → Admin approval → Automatic processing
- **Inventory Management**: Automatic available copies tracking
- **Admin Override**: Admins can directly issue/return books

## 🧪 Testing

The system includes comprehensive testing infrastructure:

### Unit Tests
- **gRPC Service Tests**: Core business logic validation
- **API Gateway Tests**: Endpoint and integration testing
- **Docker-based Testing**: Isolated test environment

### Test Execution
```bash
# Run all tests
python run_tests.py

# Run specific service tests
docker-compose -f docker-compose.test.yml up --build
```

### Sample Test Scenarios
- User authentication and authorization
- Book search and filtering
- Request workflow (create → approve → process)
- Fine calculation for overdue books
- Pagination and data loading
- Error handling and edge cases

## 📚 Documentation

- **API Documentation**: Available at http://localhost:8001/docs (Swagger UI)
- **Setup Guide**: Detailed setup instructions in SETUP.md
- **Testing Guide**: Comprehensive testing documentation in README_TESTS.md
- **Code Comments**: Inline documentation throughout the codebase

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern microservices architecture
- Inspired by real-world library management needs
- Designed for scalability and maintainability
- Comprehensive sample data for immediate testing

---

**Ready to use!** Just run `docker-compose up -d` and access http://localhost:3000 to start exploring the system.