# Database Schema Documentation

## Overview
The Library Management System uses PostgreSQL as the primary database with a normalized schema designed for efficient book lending operations, user management, and transaction tracking.

## Database: `library_db`

### Core Tables

## 1. `users` Table
**Purpose**: Store user accounts with role-based access control and library member information.

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'USER',
    
    -- Library member fields
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    address VARCHAR(255),
    membership_date DATE DEFAULT CURRENT_DATE,
    
    -- System fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

**Key Fields**:
- `user_id`: Primary key, auto-incrementing
- `username`: Unique login identifier
- `role`: 'ADMIN' or 'USER' for access control
- `is_active`: Soft delete flag for user accounts
- `membership_date`: When user joined the library

**Sample Data**: 30 users (3 admins, 27 regular users)

## 2. `books` Table
**Purpose**: Store the library's book catalog with inventory tracking.

```sql
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    genre VARCHAR(50),
    published_year INTEGER,
    available_copies INTEGER DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

**Key Fields**:
- `book_id`: Primary key, auto-incrementing
- `available_copies`: Current inventory count (1-10 per book)
- `is_deleted`: Soft delete flag for books

**Sample Data**: 104 unique books across 11 genres
- Fiction, Science Fiction, Fantasy, Mystery, Romance, Young Adult, Non-Fiction, Biography, History, Self-Help, Classic Literature

## 3. `transactions` Table
**Purpose**: Track all book borrowing and return activities with fine calculations.

```sql
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    return_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'BORROWED',
    fine_amount INTEGER DEFAULT 0
);
```

**Key Fields**:
- `transaction_type`: 'BORROW' or 'RETURN'
- `status`: 'BORROWED', 'RETURNED', 'OVERDUE'
- `due_date`: 30 days from borrow date
- `fine_amount`: ₹10 per day for overdue books

**Business Rules**:
- 30-day borrowing period
- ₹10/day fine for overdue books
- Maximum 3 books per user simultaneously
- One copy per book per user

## 4. `book_requests` Table
**Purpose**: Manage book request workflow from users to admin approval/rejection.

```sql
CREATE TABLE book_requests (
    request_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    request_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_response_date TIMESTAMP,
    admin_id INTEGER,
    notes TEXT,
    transaction_id INTEGER
);
```

**Key Fields**:
- `request_type`: 'BORROW' or 'RETURN'
- `status`: 'PENDING', 'APPROVED', 'REJECTED'
- `admin_id`: Which admin processed the request
- `transaction_id`: Links to created transaction when approved

**Workflow**:
1. User creates request → Status: 'PENDING'
2. Admin approves → Status: 'APPROVED', creates transaction
3. Admin rejects → Status: 'REJECTED' with notes

## Relationships

### Foreign Key Constraints
```sql
-- Transactions reference users and books
ALTER TABLE transactions 
ADD CONSTRAINT fk_transaction_user FOREIGN KEY (user_id) REFERENCES users(user_id);

ALTER TABLE transactions 
ADD CONSTRAINT fk_transaction_book FOREIGN KEY (book_id) REFERENCES books(book_id);

-- Book requests reference users, books, and admins
ALTER TABLE book_requests 
ADD CONSTRAINT fk_request_user FOREIGN KEY (user_id) REFERENCES users(user_id);

ALTER TABLE book_requests 
ADD CONSTRAINT fk_request_book FOREIGN KEY (book_id) REFERENCES books(book_id);

ALTER TABLE book_requests 
ADD CONSTRAINT fk_request_admin FOREIGN KEY (admin_id) REFERENCES users(user_id);

ALTER TABLE book_requests 
ADD CONSTRAINT fk_request_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id);
```

### Entity Relationships
```
users (1) ──── (M) transactions
users (1) ──── (M) book_requests
books (1) ──── (M) transactions  
books (1) ──── (M) book_requests
transactions (1) ──── (1) book_requests [optional]
```

## Indexes

### Performance Indexes
```sql
-- User lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Book searches
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_genre ON books(genre);
CREATE INDEX idx_books_not_deleted ON books(book_id) WHERE is_deleted = FALSE;

-- Transaction queries
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_book ON transactions(book_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);

-- Request management
CREATE INDEX idx_requests_user ON book_requests(user_id);
CREATE INDEX idx_requests_status ON book_requests(status);
CREATE INDEX idx_requests_date ON book_requests(request_date);
```

## Data Integrity Rules

### Business Logic Constraints
1. **User Constraints**:
   - Username and email must be unique
   - Role must be 'ADMIN' or 'USER'
   - Active users only can borrow books

2. **Book Constraints**:
   - Available copies cannot be negative
   - Soft delete prevents data loss
   - Title and author combination should be unique

3. **Transaction Constraints**:
   - User can have maximum 3 active borrowed books
   - Cannot borrow same book multiple times simultaneously
   - Due date is always 30 days from borrow date
   - Fine calculation: (days_overdue * 10) rupees

4. **Request Constraints**:
   - Only pending requests can be approved/rejected
   - Approved borrow requests create transactions
   - Return requests must reference existing transactions

## Sample Queries

### Common Operations
```sql
-- Get user's current borrowed books
SELECT b.title, b.author, t.due_date, t.fine_amount
FROM transactions t
JOIN books b ON t.book_id = b.book_id
WHERE t.user_id = ? AND t.status = 'BORROWED';

-- Check book availability
SELECT available_copies FROM books 
WHERE book_id = ? AND is_deleted = FALSE;

-- Get overdue books with fines
SELECT u.username, b.title, t.due_date, 
       CASE WHEN t.due_date < NOW() 
            THEN (EXTRACT(days FROM NOW() - t.due_date) * 10)
            ELSE 0 END as calculated_fine
FROM transactions t
JOIN users u ON t.user_id = u.user_id
JOIN books b ON t.book_id = b.book_id
WHERE t.status = 'BORROWED' AND t.due_date < NOW();

-- Get pending requests for admin
SELECT br.request_id, u.username, b.title, br.request_type, br.request_date
FROM book_requests br
JOIN users u ON br.user_id = u.user_id
JOIN books b ON br.book_id = b.book_id
WHERE br.status = 'PENDING'
ORDER BY br.request_date;
```

## Migration History

### Database Initialization Sequence
1. `01_init.sql` - Create tables and load all migrations
2. `02_seed_data.sql` - Insert users and basic data
3. `03_books_data.sql` - Insert book catalog
4. `04_transactions_data.sql` - Insert transaction history
5. `05_add_is_deleted.sql` - Add soft delete to books
6. `06_fix_duplicate_borrows.sql` - Clean duplicate transactions
7. `07_update_book_counts.sql` - Set realistic inventory (1-10 copies)
8. `08_remove_duplicate_books.sql` - Remove duplicate books (208→104)

### Data Cleanup Operations
- **Duplicate Books**: Removed duplicates while preserving foreign key integrity
- **Duplicate Transactions**: Cleaned up duplicate borrowing records
- **Book Inventory**: Updated from binary (0/1) to realistic counts (1-10)
- **Data Integrity**: All foreign keys properly maintained during cleanup

## Performance Considerations

### Query Optimization
- **Pagination**: Implemented for large result sets (transactions)
- **Indexing**: Strategic indexes on frequently queried columns
- **Soft Deletes**: Prevents data loss while maintaining performance
- **Connection Pooling**: Efficient database connection management

### Scalability Features
- **Normalized Schema**: Reduces data redundancy
- **Proper Indexing**: Fast lookups and joins
- **Timestamp Tracking**: Audit trail for all operations
- **Role-Based Access**: Secure data access patterns