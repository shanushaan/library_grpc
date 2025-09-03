# Library Management System

A modern, full-stack library management system built with React, Node.js, gRPC, and PostgreSQL featuring real-time notifications, comprehensive validation, and robust error handling.

## 🏗️ Project Structure

```
library-grpc-service/
├── frontend/                     # React Frontend Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/           # Admin-specific components
│   │   │   ├── user/            # User-specific components
│   │   │   └── common/          # Shared components
│   │   ├── pages/               # Route components
│   │   ├── store/               # Redux state management
│   │   ├── utils/               # Validation & error handling
│   │   └── styles/              # CSS styling
│   └── package.json
├── api-gateway/                 # Python FastAPI Gateway (Modular)
│   ├── routes/                  # Domain-specific route handlers
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── books.py             # Book management endpoints
│   │   ├── requests.py          # Book request endpoints
│   │   ├── transactions.py      # Transaction endpoints
│   │   ├── users.py             # User management endpoints
│   │   └── websocket.py         # WebSocket connections
│   ├── services/                # Business logic layer
│   │   ├── auth_service.py      # Authentication service
│   │   ├── book_service.py      # Book operations service
│   │   ├── request_service.py   # Request management service
│   │   └── notification_service.py # Real-time notifications
│   ├── core/                    # Core utilities & configuration
│   │   ├── grpc_client.py       # gRPC client management
│   │   ├── validation.py        # Input validation functions
│   │   ├── logging_config.py    # Structured logging setup
│   │   └── enums.py             # Status constants & enums
│   ├── tests/                   # Comprehensive test suite (100+ tests)
│   │   ├── core/                # Core function tests
│   │   ├── routes/              # API endpoint tests
│   │   ├── services/            # Business logic tests
│   │   ├── integration/         # End-to-end tests
│   │   └── unit/                # Component unit tests
│   ├── utils/                   # Test utilities & mock data
│   ├── main.py                  # FastAPI application entry
│   └── run_organized_tests.py   # Test runner with coverage
├── api-gateway-node/            # Node.js API Gateway (Alternative)
│   ├── routes/                  # Modular route handlers
│   ├── utils/                   # gRPC client utilities
│   ├── websocket.js             # WebSocket server
│   └── server.js                # Main server file
├── grpc-server/                 # Python gRPC Backend
│   ├── services/                # Business logic services
│   ├── models/                  # Database models
│   └── server.py                # gRPC server
├── db-init/                     # Database initialization
│   └── init.sql                 # Schema & sample data
├── proto/                       # Protocol Buffer definitions
│   └── library_service.proto   # gRPC service contracts
├── shared/                      # Shared database utilities
└── docker-compose.yml           # Container orchestration
```

## 🔄 Data Flow Architecture

### Modular FastAPI Gateway Architecture
```
┌─────────────────┐    HTTP/WS     ┌──────────────────────────────────────┐    gRPC      ┌─────────────────┐
│   React Client  │ ◄──────────► │         FastAPI Gateway              │ ◄─────────► │  Python gRPC    │
│                 │               │  ┌─────────────┐  ┌─────────────────┐ │             │     Server      │
│ • Redux Store   │               │  │   Routes    │  │    Services     │ │             │                 │
│ • Components    │               │  │ • auth.py   │  │ • auth_service  │ │             │ • Business Logic│
│ • Validation    │               │  │ • books.py  │  │ • book_service  │ │             │ • Data Models   │
│ • Error Bounds  │               │  │ • requests  │  │ • request_svc   │ │             │ • Database ORM  │
└─────────────────┘               │  │ • websocket │  │ • notification  │ │             │ • Validation    │
                                  │  └─────────────┘  └─────────────────┘ │             └─────────────────┘
                                  │  ┌─────────────┐  ┌─────────────────┐ │                       │
                                  │  │    Core     │  │     Tests       │ │                       ▼
                                  │  │ • grpc_client│ │ • 100+ tests    │ │              ┌─────────────────┐
                                  │  │ • validation│  │ • 5 categories  │ │              │   PostgreSQL    │
                                  │  │ • enums     │  │ • coverage      │ │              │    Database     │
                                  │  │ • logging   │  │ • organized     │ │              │                 │
                                  │  └─────────────┘  └─────────────────┘ │              │ • Users (30)    │
                                  └──────────────────────────────────────┘              │ • Books (104)   │
                                                                                          │ • Transactions  │
                                                                                          └─────────────────┘
```

### Request Flow Diagram
```
┌─────────────┐   1. HTTP Request    ┌─────────────┐   2. Route Handler   ┌─────────────┐
│   Frontend  │ ──────────────────► │   Routes    │ ──────────────────► │  Services   │
│             │                     │             │                     │             │
│ • Login     │                     │ • auth.py   │                     │ • Validate  │
│ • Search    │                     │ • books.py  │                     │ • Transform │
│ • Request   │                     │ • requests  │                     │ • Business  │
└─────────────┘                     └─────────────┘                     └─────────────┘
       ▲                                                                        │
       │                                                                        ▼
       │                            ┌─────────────┐   4. Response Data  ┌─────────────┐
       │ 5. JSON Response           │    Core     │ ◄─────────────────── │ gRPC Client │
       └──────────────────────────── │             │                     │             │
                                    │ • Validation│   3. gRPC Call      │ • Connect   │
                                    │ • Enums     │ ──────────────────► │ • Serialize │
                                    │ • Logging   │                     │ • Handle    │
                                    └─────────────┘                     └─────────────┘
```

### WebSocket Real-Time Flow
```
┌─────────────┐   WebSocket Connect   ┌─────────────┐   Store Connection   ┌─────────────┐
│   Frontend  │ ──────────────────► │  WebSocket  │ ──────────────────► │Notification │
│             │                     │   Route     │                     │  Service    │
│ • Connect   │                     │             │                     │             │
│ • Listen    │                     │ • Upgrade   │                     │ • user_id   │
│ • Display   │                     │ • Manage    │                     │ • connection│
└─────────────┘                     └─────────────┘                     └─────────────┘
       ▲                                                                        │
       │                                                                        ▼
       │ Push Notification          ┌─────────────┐   Trigger Event     ┌─────────────┐
       └──────────────────────────── │   Request   │ ◄─────────────────── │   Business  │
                                    │  Approved   │                     │   Logic     │
                                    │             │                     │             │
                                    │ • JSON msg  │                     │ • Approve   │
                                    │ • user_id   │                     │ • Reject    │
                                    │ • type      │                     │ • Issue     │
                                    └─────────────┘                     └─────────────┘
```

## ✨ Key Features

### 🔐 Authentication & Authorization
- JWT-based authentication with role-based access control
- Separate dashboards for Users and Admins
- Protected routes with automatic redirects

### 📚 Book Management
- Complete CRUD operations for book inventory
- Advanced search and filtering capabilities
- Real-time availability tracking

### 👥 User Management
- User registration and profile management
- Admin controls for user activation/deactivation
- Role-based permissions (USER/ADMIN)

### 📋 Transaction System
- Book issue/return workflow with due dates
- Automatic fine calculations for overdue books
- Transaction history and reporting

### 🔔 Real-Time Notifications
- WebSocket-powered push notifications
- Instant alerts for request approvals/rejections
- Color-coded notification system

### ✅ Enhanced Validation
- **Formik + Yup** integration for robust form validation
- **Transaction Business Rules:**
  - Duplicate request prevention
  - User borrowing limits (max 5 books)
  - Book availability validation
  - Return eligibility checks

### 🛡️ Error Handling & Recovery
- **Multi-Level Error Boundaries:**
  - App-level global protection
  - Route-level component isolation
  - Critical component crash prevention
- **Contextual Error Messages:**
  - Network errors (orange)
  - Authentication errors (red)
  - Server errors (brown)
  - Validation errors (yellow)

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd library-grpc-service
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8001
   - Database: localhost:5432

### Demo Accounts
- **Admin:** admin / admin123
- **User:** logan_baker / user123

## 🔧 Technology Stack

### Frontend
- **React 18** - Modern UI library
- **Redux Toolkit** - State management
- **Formik + Yup** - Form validation
- **Lucide React** - Icon library
- **WebSocket** - Real-time communication

### Backend
- **Node.js** - API Gateway server
- **Python** - gRPC business logic server
- **gRPC** - High-performance RPC framework
- **PostgreSQL** - Relational database

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## 📊 API Endpoints

### Authentication
- `POST /api/v1/login` - User authentication
- `POST /api/v1/logout` - User logout

### Books
- `GET /api/v1/books` - List all books
- `POST /api/v1/books` - Create new book
- `PUT /api/v1/books/:id` - Update book
- `DELETE /api/v1/books/:id` - Delete book

### Transactions
- `GET /api/v1/transactions` - List transactions
- `POST /api/v1/user/book-request` - Create book request
- `PUT /api/v1/admin/requests/:id/approve` - Approve request
- `PUT /api/v1/admin/requests/:id/reject` - Reject request

### Users
- `GET /api/v1/users` - List users (Admin only)
- `POST /api/v1/users` - Create user (Admin only)
- `PUT /api/v1/users/:id` - Update user (Admin only)

## 🔄 Real-Time Features

### WebSocket Integration
- **Connection:** `ws://localhost:8001?userId={user_id}`
- **Events:** Request approvals, rejections, system notifications
- **Auto-reconnection:** Handles connection drops gracefully

### Notification System
- **Toast Notifications:** Temporary success/error messages
- **Bell Notifications:** Persistent notification history
- **Color Coding:** Visual distinction for different message types

## 🛠️ Development Workflow

### Adding New Features
1. **Frontend:** Create components in appropriate directories
2. **API Gateway:** Add routes in `api-gateway-node/routes/`
3. **Backend:** Implement gRPC services in `grpc-server/services/`
4. **Database:** Update models and migrations

### Error Boundary Implementation
```javascript
// Wrap components with ErrorBoundary
<ErrorBoundary fallbackMessage="Component unavailable">
  <YourComponent />
</ErrorBoundary>
```

### Validation Schema Example
```javascript
// utils/validationSchemas.js
export const bookSchema = Yup.object({
  title: Yup.string().min(2).max(100).required(),
  author: Yup.string().min(2).max(50).required(),
  // ... more validation rules
});
```

## 📈 Performance & Scalability

- **Component-level error boundaries** prevent cascading failures
- **Redux state management** for efficient data flow
- **gRPC** for high-performance backend communication
- **WebSocket** for real-time updates without polling
- **Modular architecture** for easy feature additions

## 🔒 Security Features

- JWT token-based authentication
- Role-based access control
- Input validation on client and server
- SQL injection prevention through ORM
- CORS configuration for API security

## 🧪 Testing & Quality Assurance

### Comprehensive Test Suite (100+ Tests)
```
tests/
├── core/          # Input validation & utility tests (9 tests)
├── routes/        # API endpoint tests (34 tests)
├── services/      # Business logic tests (20 tests)
├── integration/   # End-to-end workflow tests (1 test)
└── unit/          # Component & error handling tests (36 tests)
```

### Test Categories & Coverage
- **Core Tests**: Validation functions, enums, utilities
- **Route Tests**: Authentication, CRUD operations, error responses
- **Service Tests**: Business rules, gRPC integration, admin restrictions
- **Integration Tests**: Complete user workflows (login → request → approval)
- **Unit Tests**: Individual components, WebSocket handling, error scenarios

### Running Tests
```bash
# Run organized test suite with coverage
cd api-gateway && python run_organized_tests.py

# Run specific test categories
pytest tests/core/ -v          # Core validation tests
pytest tests/routes/ -v        # API endpoint tests
pytest tests/services/ -v      # Business logic tests

# Test admin restrictions
pytest tests/services/test_admin_restrictions.py -v
```

## 🔒 Business Rules & Security

### Admin Restrictions
- **Admin users cannot request book issues** (enforced at service layer)
- **Dynamic role validation** (queries actual user role from database)
- **Proper HTTP status codes** (403 Forbidden for admin restrictions)

### Input Validation
- **Pydantic models** with custom validators
- **Enum constants** for request types, statuses, user roles
- **Server-side validation** prevents data corruption

### Error Handling
- **Structured logging** with JSON formatter and context
- **Graceful degradation** when services are unavailable
- **Comprehensive exception handling** with proper HTTP codes

## 📝 Recent Enhancements

### v3.0 Features (Latest)
- ✅ **Modular FastAPI Architecture** - Separated routes, services, core modules
- ✅ **Comprehensive Test Suite** - 100+ tests with organized runner
- ✅ **Admin Business Rules** - Admins cannot request book issues
- ✅ **Enum Constants** - Centralized status values and types
- ✅ **Structured Logging** - JSON formatter with contextual information
- ✅ **Input Validation** - Enhanced Pydantic models with custom validators
- ✅ **Error Boundaries** - Graceful failure handling and recovery
- ✅ **WebSocket Management** - Real-time notification service
- ✅ **Test Coverage** - 94% unit test coverage with async support
- ✅ **Production Ready** - Containerized, tested, and documented

### v2.0 Features
- ✅ Enhanced form validation with Formik + Yup
- ✅ Multi-level error boundaries
- ✅ Real-time WebSocket notifications
- ✅ Transaction business rule validation
- ✅ Color-coded notification system
- ✅ Route-level lazy loading (React.lazy + Suspense)
- ✅ Responsive burger menu for mobile devices

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.