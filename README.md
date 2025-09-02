# Library Management System

A modern, full-stack library management system built with React, Node.js, gRPC, and PostgreSQL featuring real-time notifications, comprehensive validation, and robust error handling.

## 🏗️ Project Structure

```
library-grpc-service/
├── frontend/                     # React Frontend Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/           # Admin-specific components
│   │   │   │   ├── BookRequests.js
│   │   │   │   ├── BooksManagement.js
│   │   │   │   ├── DashboardOverview.js
│   │   │   │   ├── TransactionsManagement.js
│   │   │   │   └── UsersManagement.js
│   │   │   ├── user/            # User-specific components
│   │   │   │   ├── BookSearch.js
│   │   │   │   ├── MyBooks.js
│   │   │   │   └── UserProfile.js
│   │   │   └── common/          # Shared components
│   │   │       ├── ErrorBoundary.js
│   │   │       ├── NotificationBell.js
│   │   │       ├── DataTable.js
│   │   │       └── DashboardLayout.js
│   │   ├── pages/               # Route components
│   │   ├── store/               # Redux state management
│   │   ├── utils/               # Validation & error handling
│   │   └── styles/              # CSS styling
│   └── package.json
├── api-gateway-node/            # Node.js API Gateway
│   ├── routes/                  # Modular route handlers
│   │   ├── auth.js
│   │   ├── books.js
│   │   ├── requests.js
│   │   ├── transactions.js
│   │   └── users.js
│   ├── utils/                   # gRPC client utilities
│   ├── websocket.js             # WebSocket server
│   └── server.js                # Main server file
├── grpc-server/                 # Python gRPC Backend
│   ├── services/                # Business logic services
│   ├── models/                  # Database models
│   └── server.py                # gRPC server
├── shared/                      # Shared database utilities
└── docker-compose.yml           # Container orchestration
```

## 🔄 Data Flow Architecture

```
┌─────────────────┐    HTTP/WS     ┌──────────────────┐    gRPC      ┌─────────────────┐
│   React Client  │ ◄──────────► │  Node.js Gateway │ ◄─────────► │  Python gRPC    │
│                 │               │                  │             │     Server      │
│ • Redux Store   │               │ • Route Handlers │             │ • Business Logic│
│ • Components    │               │ • WebSocket      │             │ • Data Models   │
│ • Validation    │               │ • Error Handling │             │ • Database ORM  │
└─────────────────┘               └──────────────────┘             └─────────────────┘
                                                                            │
                                                                            ▼
                                                                   ┌─────────────────┐
                                                                   │   PostgreSQL    │
                                                                   │    Database     │
                                                                   └─────────────────┘
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

## 📝 Recent Enhancements

### v2.0 Features
- ✅ Enhanced form validation with Formik + Yup
- ✅ Comprehensive error handling system
- ✅ Multi-level error boundaries
- ✅ Real-time WebSocket notifications
- ✅ Transaction business rule validation
- ✅ Modular API Gateway architecture
- ✅ Color-coded notification system

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.