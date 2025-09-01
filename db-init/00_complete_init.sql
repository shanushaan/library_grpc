-- Complete Library Management System Database Initialization
-- Single file with all tables, data, and optimizations

-- ============================================================================
-- 1. CREATE TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
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

CREATE TABLE IF NOT EXISTS books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    genre VARCHAR(50),
    published_year INTEGER,
    available_copies INTEGER DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS transactions (
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

CREATE TABLE IF NOT EXISTS book_requests (
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

-- ============================================================================
-- 2. INSERT USERS (30 total: 3 admins + 27 users)
-- ============================================================================

INSERT INTO users (username, email, password_hash, role, full_name, phone, address) VALUES
-- Admin users
('admin', 'admin@library.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'ADMIN', 'System Administrator', '555-0001', '123 Admin St'),
('librarian', 'librarian@library.com', 'c6ba91b90d922e159893f46c387e5dc1b3dc5c101a5a4522f03b987177a24a91', 'ADMIN', 'Head Librarian', '555-0002', '456 Library Ave'),
('manager', 'manager@library.com', '1c142b2d01aa34e9a36bde480645a57fd69e14155dacfab5a3f9257b77fdc8d8', 'ADMIN', 'Library Manager', '555-0003', '789 Management Blvd'),

-- Regular users
('john_user', 'john@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'John Smith', '555-1001', '101 User Lane'),
('jane_smith', 'jane@email.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'USER', 'Jane Smith', '555-1002', '102 Reader Road'),
('mike_brown', 'mike@email.com', 'e258d248fda94c63753607f7c4494ee0fcbe92f1a76bfdac795c9d84101eb317', 'USER', 'Mike Brown', '555-1003', '103 Book Street'),
('sarah_davis', 'sarah@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Sarah Davis', '555-1004', '104 Novel Avenue'),
('tom_wilson', 'tom@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Tom Wilson', '555-1005', '105 Story Circle'),
('lisa_garcia', 'lisa@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Lisa Garcia', '555-1006', '106 Fiction Drive'),
('david_martinez', 'david@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'David Martinez', '555-1007', '107 Literature Lane'),
('amy_rodriguez', 'amy@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Amy Rodriguez', '555-1008', '108 Reading Road'),
('chris_lee', 'chris@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Chris Lee', '555-1009', '109 Chapter Court'),
('emma_taylor', 'emma@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Emma Taylor', '555-1010', '110 Verse Vista'),
('ryan_anderson', 'ryan@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Ryan Anderson', '555-1011', '111 Prose Place'),
('olivia_thomas', 'olivia@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Olivia Thomas', '555-1012', '112 Epic Elm'),
('alex_jackson', 'alex@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Alex Jackson', '555-1013', '113 Saga Street'),
('sophia_white', 'sophia@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Sophia White', '555-1014', '114 Tale Terrace'),
('james_harris', 'james@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'James Harris', '555-1015', '115 Fable Falls'),
('mia_clark', 'mia@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Mia Clark', '555-1016', '116 Legend Lane'),
('noah_lewis', 'noah@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Noah Lewis', '555-1017', '117 Myth Manor'),
('ava_robinson', 'ava@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Ava Robinson', '555-1018', '118 Ballad Blvd'),
('william_walker', 'william@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'William Walker', '555-1019', '119 Sonnet Square'),
('isabella_hall', 'isabella@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Isabella Hall', '555-1020', '120 Haiku Heights'),
('benjamin_allen', 'benjamin@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Benjamin Allen', '555-1021', '121 Limerick Loop'),
('charlotte_young', 'charlotte@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Charlotte Young', '555-1022', '122 Ode Oak'),
('lucas_king', 'lucas@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Lucas King', '555-1023', '123 Rhyme Ridge'),
('amelia_wright', 'amelia@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Amelia Wright', '555-1024', '124 Stanza Street'),
('henry_lopez', 'henry@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Henry Lopez', '555-1025', '125 Couplet Court'),
('harper_hill', 'harper@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Harper Hill', '555-1026', '126 Quatrain Quarter'),
('mason_green', 'mason@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Mason Green', '555-1027', '127 Verse Valley'),
('evelyn_adams', 'evelyn@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Evelyn Adams', '555-1028', '128 Meter Meadow'),
('logan_baker', 'logan@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Logan Baker', '555-1029', '129 Rhythm Road'),
('abigail_gonzalez', 'abigail@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'USER', 'Abigail Gonzalez', '555-1030', '130 Cadence Circle');

-- ============================================================================
-- 3. INSERT BOOKS (104 unique books with realistic inventory 1-10 copies)
-- ============================================================================

INSERT INTO books (title, author, genre, published_year, available_copies) VALUES
-- Fiction (15 books)
('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 1925, 5),
('To Kill a Mockingbird', 'Harper Lee', 'Fiction', 1960, 4),
('Pride and Prejudice', 'Jane Austen', 'Fiction', 1813, 3),
('The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 1951, 6),
('Lord of the Flies', 'William Golding', 'Fiction', 1954, 4),
('Of Mice and Men', 'John Steinbeck', 'Fiction', 1937, 3),
('The Grapes of Wrath', 'John Steinbeck', 'Fiction', 1939, 2),
('Wuthering Heights', 'Emily Brontë', 'Fiction', 1847, 3),
('Jane Eyre', 'Charlotte Brontë', 'Fiction', 1847, 4),
('Great Expectations', 'Charles Dickens', 'Fiction', 1861, 3),
('A Tale of Two Cities', 'Charles Dickens', 'Fiction', 1859, 5),
('The Adventures of Huckleberry Finn', 'Mark Twain', 'Fiction', 1884, 4),
('Moby Dick', 'Herman Melville', 'Fiction', 1851, 2),
('The Scarlet Letter', 'Nathaniel Hawthorne', 'Fiction', 1850, 3),
('Frankenstein', 'Mary Shelley', 'Fiction', 1818, 4),

-- Science Fiction (10 books)
('1984', 'George Orwell', 'Science Fiction', 1949, 6),
('Brave New World', 'Aldous Huxley', 'Science Fiction', 1932, 4),
('Fahrenheit 451', 'Ray Bradbury', 'Science Fiction', 1953, 5),
('Dune', 'Frank Herbert', 'Science Fiction', 1965, 3),
('Foundation', 'Isaac Asimov', 'Science Fiction', 1951, 4),
('The Hitchhiker''s Guide to the Galaxy', 'Douglas Adams', 'Science Fiction', 1979, 5),
('Ender''s Game', 'Orson Scott Card', 'Science Fiction', 1985, 4),
('The Martian', 'Andy Weir', 'Science Fiction', 2011, 6),
('Neuromancer', 'William Gibson', 'Science Fiction', 1984, 3),
('The Time Machine', 'H.G. Wells', 'Science Fiction', 1895, 2),

-- Fantasy (10 books)
('The Lord of the Rings', 'J.R.R. Tolkien', 'Fantasy', 1954, 8),
('The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 1937, 6),
('Harry Potter and the Sorcerer''s Stone', 'J.K. Rowling', 'Fantasy', 1997, 10),
('Harry Potter and the Chamber of Secrets', 'J.K. Rowling', 'Fantasy', 1998, 8),
('Harry Potter and the Prisoner of Azkaban', 'J.K. Rowling', 'Fantasy', 1999, 7),
('A Game of Thrones', 'George R.R. Martin', 'Fantasy', 1996, 5),
('The Chronicles of Narnia', 'C.S. Lewis', 'Fantasy', 1950, 6),
('The Name of the Wind', 'Patrick Rothfuss', 'Fantasy', 2007, 4),
('The Way of Kings', 'Brandon Sanderson', 'Fantasy', 2010, 3),
('Mistborn', 'Brandon Sanderson', 'Fantasy', 2006, 4),

-- Mystery/Thriller (10 books)
('The Girl with the Dragon Tattoo', 'Stieg Larsson', 'Mystery', 2005, 5),
('Gone Girl', 'Gillian Flynn', 'Thriller', 2012, 6),
('The Da Vinci Code', 'Dan Brown', 'Thriller', 2003, 4),
('And Then There Were None', 'Agatha Christie', 'Mystery', 1939, 5),
('The Murder of Roger Ackroyd', 'Agatha Christie', 'Mystery', 1926, 3),
('The Big Sleep', 'Raymond Chandler', 'Mystery', 1939, 2),
('In Cold Blood', 'Truman Capote', 'True Crime', 1966, 3),
('The Silence of the Lambs', 'Thomas Harris', 'Thriller', 1988, 4),
('The Shining', 'Stephen King', 'Horror', 1977, 5),
('It', 'Stephen King', 'Horror', 1986, 4),

-- Romance (8 books)
('Outlander', 'Diana Gabaldon', 'Romance', 1991, 4),
('The Notebook', 'Nicholas Sparks', 'Romance', 1996, 5),
('Me Before You', 'Jojo Moyes', 'Romance', 2012, 6),
('The Fault in Our Stars', 'John Green', 'Romance', 2012, 7),
('Sense and Sensibility', 'Jane Austen', 'Romance', 1811, 3),
('Emma', 'Jane Austen', 'Romance', 1815, 3),
('Persuasion', 'Jane Austen', 'Romance', 1817, 2),
('Gone with the Wind', 'Margaret Mitchell', 'Romance', 1936, 4),

-- Non-Fiction (10 books)
('Sapiens', 'Yuval Noah Harari', 'Non-Fiction', 2011, 5),
('Educated', 'Tara Westover', 'Memoir', 2018, 6),
('Becoming', 'Michelle Obama', 'Biography', 2018, 7),
('The Immortal Life of Henrietta Lacks', 'Rebecca Skloot', 'Science', 2010, 4),
('A Brief History of Time', 'Stephen Hawking', 'Science', 1988, 3),
('The Art of War', 'Sun Tzu', 'Philosophy', 500, 2),
('Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology', 2011, 4),
('The Power of Habit', 'Charles Duhigg', 'Self-Help', 2012, 5),
('Atomic Habits', 'James Clear', 'Self-Help', 2018, 8),
('The 7 Habits of Highly Effective People', 'Stephen Covey', 'Self-Help', 1989, 6),

-- History/Biography (7 books)
('The Guns of August', 'Barbara Tuchman', 'History', 1962, 3),
('A People''s History of the United States', 'Howard Zinn', 'History', 1980, 4),
('The Diary of a Young Girl', 'Anne Frank', 'History', 1947, 5),
('Band of Brothers', 'Stephen Ambrose', 'History', 1992, 3),
('The Wright Brothers', 'David McCullough', 'Biography', 2015, 2),
('John Adams', 'David McCullough', 'Biography', 2001, 3),
('Alexander Hamilton', 'Ron Chernow', 'Biography', 2004, 4),

-- Young Adult (8 books)
('The Hunger Games', 'Suzanne Collins', 'Young Adult', 2008, 8),
('Catching Fire', 'Suzanne Collins', 'Young Adult', 2009, 6),
('Mockingjay', 'Suzanne Collins', 'Young Adult', 2010, 5),
('Divergent', 'Veronica Roth', 'Young Adult', 2011, 5),
('The Maze Runner', 'James Dashner', 'Young Adult', 2009, 4),
('Thirteen Reasons Why', 'Jay Asher', 'Young Adult', 2007, 3),
('Looking for Alaska', 'John Green', 'Young Adult', 2005, 4),
('The Perks of Being a Wallflower', 'Stephen Chbosky', 'Young Adult', 1999, 5),

-- Classic Literature (10 books)
('War and Peace', 'Leo Tolstoy', 'Classic', 1869, 2),
('Anna Karenina', 'Leo Tolstoy', 'Classic', 1877, 3),
('Crime and Punishment', 'Fyodor Dostoevsky', 'Classic', 1866, 3),
('The Brothers Karamazov', 'Fyodor Dostoevsky', 'Classic', 1880, 2),
('One Hundred Years of Solitude', 'Gabriel García Márquez', 'Classic', 1967, 3),
('The Odyssey', 'Homer', 'Classic', -800, 4),
('The Iliad', 'Homer', 'Classic', -750, 3),
('Don Quixote', 'Miguel de Cervantes', 'Classic', 1605, 2),
('Ulysses', 'James Joyce', 'Classic', 1922, 2),
('The Canterbury Tales', 'Geoffrey Chaucer', 'Classic', 1387, 2),

-- Contemporary Fiction (10 books)
('The Kite Runner', 'Khaled Hosseini', 'Contemporary', 2003, 5),
('A Thousand Splendid Suns', 'Khaled Hosseini', 'Contemporary', 2007, 4),
('The Book Thief', 'Markus Zusak', 'Contemporary', 2005, 6),
('Life of Pi', 'Yann Martel', 'Contemporary', 2001, 4),
('The Curious Incident of the Dog in the Night-Time', 'Mark Haddon', 'Contemporary', 2003, 5),
('Never Let Me Go', 'Kazuo Ishiguro', 'Contemporary', 2005, 3),
('The Road', 'Cormac McCarthy', 'Contemporary', 2006, 4),
('Atonement', 'Ian McEwan', 'Contemporary', 2001, 3),
('The Lovely Bones', 'Alice Sebold', 'Contemporary', 2002, 4),
('Where the Crawdads Sing', 'Delia Owens', 'Contemporary', 2018, 7),

-- Poetry & Drama (6 books)
('The Complete Works of William Shakespeare', 'William Shakespeare', 'Drama', 1623, 5),
('Leaves of Grass', 'Walt Whitman', 'Poetry', 1855, 2),
('The Waste Land', 'T.S. Eliot', 'Poetry', 1922, 2),
('Death of a Salesman', 'Arthur Miller', 'Drama', 1949, 3),
('A Streetcar Named Desire', 'Tennessee Williams', 'Drama', 1947, 3),
('The Glass Menagerie', 'Tennessee Williams', 'Drama', 1944, 2);

-- ============================================================================
-- 4. INSERT SAMPLE TRANSACTIONS (Realistic borrowing history)
-- ============================================================================

INSERT INTO transactions (user_id, book_id, transaction_type, transaction_date, due_date, return_date, status, fine_amount) VALUES
-- Active borrowings (currently borrowed books)
(4, 1, 'BORROW', '2024-01-15 10:30:00', '2024-02-14 10:30:00', NULL, 'BORROWED', 0),
(5, 15, 'BORROW', '2024-01-20 14:15:00', '2024-02-19 14:15:00', NULL, 'BORROWED', 0),
(6, 28, 'BORROW', '2024-01-25 09:45:00', '2024-02-24 09:45:00', NULL, 'BORROWED', 0),

-- Overdue books (with fines)
(7, 42, 'BORROW', '2023-12-01 11:00:00', '2023-12-31 11:00:00', NULL, 'BORROWED', 150),
(8, 55, 'BORROW', '2023-12-10 16:20:00', '2024-01-09 16:20:00', NULL, 'BORROWED', 60),

-- Returned books (completed transactions)
(4, 16, 'BORROW', '2023-11-01 10:00:00', '2023-12-01 10:00:00', '2023-11-28 15:30:00', 'RETURNED', 0),
(5, 29, 'BORROW', '2023-11-05 14:00:00', '2023-12-05 14:00:00', '2023-12-03 10:15:00', 'RETURNED', 0),
(6, 43, 'BORROW', '2023-11-10 09:30:00', '2023-12-10 09:30:00', '2023-12-15 11:45:00', 'RETURNED', 50),

-- More transaction history for testing
(9, 2, 'BORROW', '2023-10-15 13:20:00', '2023-11-14 13:20:00', '2023-11-10 16:00:00', 'RETURNED', 0),
(10, 17, 'BORROW', '2023-10-20 11:45:00', '2023-11-19 11:45:00', '2023-11-18 14:30:00', 'RETURNED', 0),
(11, 30, 'BORROW', '2023-10-25 15:10:00', '2023-11-24 15:10:00', '2023-11-30 09:20:00', 'RETURNED', 60),
(12, 44, 'BORROW', '2023-09-01 10:15:00', '2023-09-30 10:15:00', '2023-09-28 12:45:00', 'RETURNED', 0),
(13, 56, 'BORROW', '2023-09-05 14:30:00', '2023-10-05 14:30:00', '2023-10-08 16:20:00', 'RETURNED', 30);

-- ============================================================================
-- 5. INSERT SAMPLE BOOK REQUESTS (Pending and processed requests)
-- ============================================================================

INSERT INTO book_requests (user_id, book_id, request_type, status, request_date, admin_response_date, admin_id, notes) VALUES
-- Pending requests
(14, 3, 'BORROW', 'PENDING', '2024-01-28 10:30:00', NULL, NULL, 'Would like to read this classic'),
(15, 31, 'BORROW', 'PENDING', '2024-01-28 14:15:00', NULL, NULL, 'Interested in fantasy series'),
(16, 45, 'BORROW', 'PENDING', '2024-01-29 09:20:00', NULL, NULL, 'Need for book club discussion'),

-- Approved requests (linked to transactions)
(17, 18, 'BORROW', 'APPROVED', '2024-01-25 11:00:00', '2024-01-25 11:30:00', 1, 'Approved - book available'),
(18, 32, 'BORROW', 'APPROVED', '2024-01-26 13:45:00', '2024-01-26 14:00:00', 2, 'Approved for student research'),

-- Rejected requests
(19, 1, 'BORROW', 'REJECTED', '2024-01-27 15:20:00', '2024-01-27 16:00:00', 1, 'Book currently unavailable - all copies borrowed');

-- ============================================================================
-- 6. CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Book indexes
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);
CREATE INDEX IF NOT EXISTS idx_books_not_deleted ON books(book_id) WHERE is_deleted = FALSE;

-- Transaction indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_book ON transactions(book_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_due_date ON transactions(due_date);

-- Request indexes
CREATE INDEX IF NOT EXISTS idx_requests_user ON book_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_requests_book ON book_requests(book_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON book_requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_date ON book_requests(request_date);

-- ============================================================================
-- 7. VERIFY DATA INTEGRITY
-- ============================================================================

-- Display summary statistics
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Books', COUNT(*) FROM books
UNION ALL  
SELECT 'Transactions', COUNT(*) FROM transactions
UNION ALL
SELECT 'Book Requests', COUNT(*) FROM book_requests;

-- Verify no duplicate books
SELECT COUNT(*) as unique_books, COUNT(DISTINCT title || author) as unique_title_author_pairs FROM books;

-- Show genre distribution
SELECT genre, COUNT(*) as book_count FROM books GROUP BY genre ORDER BY book_count DESC;