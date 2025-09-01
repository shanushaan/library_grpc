-- Complete Library Management System Database Initialization
-- Single file with all tables, data, and optimizations
--
-- PASSWORD MAPPINGS (SHA-256 hashes):
-- admin123    -> 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- lib123     -> 6518454a49ab2912238b510b2221f0fc1ce404986d3fb94bb34311ff6069d467
-- mgr123     -> 49a0ac18e26df0b0724f5ac5837e436b336527485fc0a388f578913d6ee70e67
-- user123    -> e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446
-- jane123    -> a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
-- mike123    -> e258d248fda94c63753607f7c4494ee0fcbe92f1a76bfdac795c9d84101eb317

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
-- Admin users (admin123, lib123, mgr123)
('admin', 'admin@library.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'ADMIN', 'System Administrator', '555-0001', '123 Admin St'),
('librarian', 'librarian@library.com', '6518454a49ab2912238b510b2221f0fc1ce404986d3fb94bb34311ff6069d467', 'ADMIN', 'Head Librarian', '555-0002', '456 Library Ave'),
('manager', 'manager@library.com', '49a0ac18e26df0b0724f5ac5837e436b336527485fc0a388f578913d6ee70e67', 'ADMIN', 'Library Manager', '555-0003', '789 Management Blvd'),

-- Regular users (user123, jane123, mike123)
('john_user', 'john@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'John Smith', '555-1001', '101 User Lane'),
('jane_smith', 'jane@email.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'USER', 'Jane Smith', '555-1002', '102 Reader Road'),
('mike_brown', 'mike@email.com', 'e258d248fda94c63753607f7c4494ee0fcbe92f1a76bfdac795c9d84101eb317', 'USER', 'Mike Brown', '555-1003', '103 Book Street'),
-- All other users use user123 password for simplicity
('sarah_davis', 'sarah@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Sarah Davis', '555-1004', '104 Novel Avenue'),
('tom_wilson', 'tom@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Tom Wilson', '555-1005', '105 Story Circle'),
('lisa_garcia', 'lisa@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Lisa Garcia', '555-1006', '106 Fiction Drive'),
('david_martinez', 'david@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'David Martinez', '555-1007', '107 Literature Lane'),
('amy_rodriguez', 'amy@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Amy Rodriguez', '555-1008', '108 Reading Road'),
('chris_lee', 'chris@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Chris Lee', '555-1009', '109 Chapter Court'),
('emma_taylor', 'emma@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Emma Taylor', '555-1010', '110 Verse Vista'),
('ryan_anderson', 'ryan@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Ryan Anderson', '555-1011', '111 Prose Place'),
('olivia_thomas', 'olivia@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Olivia Thomas', '555-1012', '112 Epic Elm'),
('alex_jackson', 'alex@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Alex Jackson', '555-1013', '113 Saga Street'),
('sophia_white', 'sophia@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Sophia White', '555-1014', '114 Tale Terrace'),
('james_harris', 'james@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'James Harris', '555-1015', '115 Fable Falls'),
('mia_clark', 'mia@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Mia Clark', '555-1016', '116 Legend Lane'),
('noah_lewis', 'noah@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Noah Lewis', '555-1017', '117 Myth Manor'),
('ava_robinson', 'ava@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Ava Robinson', '555-1018', '118 Ballad Blvd'),
('william_walker', 'william@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'William Walker', '555-1019', '119 Sonnet Square'),
('isabella_hall', 'isabella@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Isabella Hall', '555-1020', '120 Haiku Heights'),
('benjamin_allen', 'benjamin@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Benjamin Allen', '555-1021', '121 Limerick Loop'),
('charlotte_young', 'charlotte@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Charlotte Young', '555-1022', '122 Ode Oak'),
('lucas_king', 'lucas@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Lucas King', '555-1023', '123 Rhyme Ridge'),
('amelia_wright', 'amelia@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Amelia Wright', '555-1024', '124 Stanza Street'),
('henry_lopez', 'henry@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Henry Lopez', '555-1025', '125 Couplet Court'),
('harper_hill', 'harper@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Harper Hill', '555-1026', '126 Quatrain Quarter'),
('mason_green', 'mason@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Mason Green', '555-1027', '127 Verse Valley'),
('evelyn_adams', 'evelyn@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Evelyn Adams', '555-1028', '128 Meter Meadow'),
('logan_baker', 'logan@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Logan Baker', '555-1029', '129 Rhythm Road'),
('abigail_gonzalez', 'abigail@email.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'USER', 'Abigail Gonzalez', '555-1030', '130 Cadence Circle');

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
-- 4. INSERT 100 SAMPLE TRANSACTIONS (Comprehensive borrowing history)
-- ============================================================================

INSERT INTO transactions (user_id, book_id, transaction_type, transaction_date, due_date, return_date, status, fine_amount) VALUES
-- Current active borrowings (15 books currently borrowed)
(4, 1, 'BORROW', '2024-01-15 10:30:00', '2024-02-14 10:30:00', NULL, 'BORROWED', 0),
(5, 15, 'BORROW', '2024-01-20 14:15:00', '2024-02-19 14:15:00', NULL, 'BORROWED', 0),
(6, 28, 'BORROW', '2024-01-25 09:45:00', '2024-02-24 09:45:00', NULL, 'BORROWED', 0),
(9, 33, 'BORROW', '2024-01-18 11:20:00', '2024-02-17 11:20:00', NULL, 'BORROWED', 0),
(10, 45, 'BORROW', '2024-01-22 16:30:00', '2024-02-21 16:30:00', NULL, 'BORROWED', 0),
(11, 67, 'BORROW', '2024-01-28 13:45:00', '2024-02-27 13:45:00', NULL, 'BORROWED', 0),
(12, 78, 'BORROW', '2024-01-30 10:15:00', '2024-02-29 10:15:00', NULL, 'BORROWED', 0),
(13, 89, 'BORROW', '2024-01-26 14:20:00', '2024-02-25 14:20:00', NULL, 'BORROWED', 0),
(14, 12, 'BORROW', '2024-01-29 09:30:00', '2024-02-28 09:30:00', NULL, 'BORROWED', 0),
(15, 23, 'BORROW', '2024-01-31 15:45:00', '2024-03-01 15:45:00', NULL, 'BORROWED', 0),
(16, 34, 'BORROW', '2024-01-27 12:10:00', '2024-02-26 12:10:00', NULL, 'BORROWED', 0),
(17, 56, 'BORROW', '2024-01-24 17:25:00', '2024-02-23 17:25:00', NULL, 'BORROWED', 0),
(18, 71, 'BORROW', '2024-01-21 08:40:00', '2024-02-20 08:40:00', NULL, 'BORROWED', 0),
(19, 82, 'BORROW', '2024-01-23 11:55:00', '2024-02-22 11:55:00', NULL, 'BORROWED', 0),
(20, 93, 'BORROW', '2024-01-19 14:35:00', '2024-02-18 14:35:00', NULL, 'BORROWED', 0),

-- Overdue books (8 books with accumulated fines)
(7, 42, 'BORROW', '2023-12-01 11:00:00', '2023-12-31 11:00:00', NULL, 'BORROWED', 320),
(8, 55, 'BORROW', '2023-12-10 16:20:00', '2024-01-09 16:20:00', NULL, 'BORROWED', 230),
(21, 16, 'BORROW', '2023-12-15 09:30:00', '2024-01-14 09:30:00', NULL, 'BORROWED', 180),
(22, 27, 'BORROW', '2023-12-20 13:45:00', '2024-01-19 13:45:00', NULL, 'BORROWED', 130),
(23, 38, 'BORROW', '2023-12-25 10:15:00', '2024-01-24 10:15:00', NULL, 'BORROWED', 80),
(24, 49, 'BORROW', '2023-12-28 14:30:00', '2024-01-27 14:30:00', NULL, 'BORROWED', 50),
(25, 61, 'BORROW', '2024-01-02 11:20:00', '2024-02-01 11:20:00', NULL, 'BORROWED', 10),
(26, 72, 'BORROW', '2024-01-05 16:40:00', '2024-02-04 16:40:00', NULL, 'BORROWED', 0),

-- Recently returned books (December 2023 - January 2024) - 25 transactions
(4, 16, 'BORROW', '2023-11-01 10:00:00', '2023-12-01 10:00:00', '2023-11-28 15:30:00', 'RETURNED', 0),
(5, 29, 'BORROW', '2023-11-05 14:00:00', '2023-12-05 14:00:00', '2023-12-03 10:15:00', 'RETURNED', 0),
(6, 43, 'BORROW', '2023-11-10 09:30:00', '2023-12-10 09:30:00', '2023-12-15 11:45:00', 'RETURNED', 50),
(9, 2, 'BORROW', '2023-10-15 13:20:00', '2023-11-14 13:20:00', '2023-11-10 16:00:00', 'RETURNED', 0),
(10, 17, 'BORROW', '2023-10-20 11:45:00', '2023-11-19 11:45:00', '2023-11-18 14:30:00', 'RETURNED', 0),
(11, 30, 'BORROW', '2023-10-25 15:10:00', '2023-11-24 15:10:00', '2023-11-30 09:20:00', 'RETURNED', 60),
(12, 44, 'BORROW', '2023-09-01 10:15:00', '2023-09-30 10:15:00', '2023-09-28 12:45:00', 'RETURNED', 0),
(13, 56, 'BORROW', '2023-09-05 14:30:00', '2023-10-05 14:30:00', '2023-10-08 16:20:00', 'RETURNED', 30),
(14, 3, 'BORROW', '2023-11-15 12:00:00', '2023-12-15 12:00:00', '2023-12-10 09:30:00', 'RETURNED', 0),
(15, 18, 'BORROW', '2023-11-20 16:45:00', '2023-12-20 16:45:00', '2023-12-18 14:20:00', 'RETURNED', 0),
(16, 31, 'BORROW', '2023-11-25 11:30:00', '2023-12-25 11:30:00', '2023-12-30 10:15:00', 'RETURNED', 50),
(17, 47, 'BORROW', '2023-12-01 13:15:00', '2023-12-31 13:15:00', '2023-12-28 16:45:00', 'RETURNED', 0),
(18, 59, 'BORROW', '2023-12-05 10:45:00', '2024-01-04 10:45:00', '2024-01-02 12:30:00', 'RETURNED', 0),
(19, 64, 'BORROW', '2023-12-10 15:20:00', '2024-01-09 15:20:00', '2024-01-12 11:10:00', 'RETURNED', 30),
(20, 75, 'BORROW', '2023-12-15 09:40:00', '2024-01-14 09:40:00', '2024-01-10 14:25:00', 'RETURNED', 0),
(27, 86, 'BORROW', '2023-12-20 14:55:00', '2024-01-19 14:55:00', '2024-01-15 16:30:00', 'RETURNED', 0),
(28, 91, 'BORROW', '2023-12-25 11:25:00', '2024-01-24 11:25:00', '2024-01-20 13:45:00', 'RETURNED', 0),
(29, 4, 'BORROW', '2023-11-08 16:10:00', '2023-12-08 16:10:00', '2023-12-05 10:20:00', 'RETURNED', 0),
(30, 19, 'BORROW', '2023-11-12 12:35:00', '2023-12-12 12:35:00', '2023-12-15 15:40:00', 'RETURNED', 30),
(31, 32, 'BORROW', '2023-11-18 14:50:00', '2023-12-18 14:50:00', '2023-12-14 09:15:00', 'RETURNED', 0),
(32, 48, 'BORROW', '2023-11-22 10:25:00', '2023-12-22 10:25:00', '2023-12-25 12:50:00', 'RETURNED', 30),
(33, 60, 'BORROW', '2023-11-28 13:40:00', '2023-12-28 13:40:00', '2023-12-22 16:25:00', 'RETURNED', 0),
(4, 73, 'BORROW', '2023-12-02 15:15:00', '2024-01-01 15:15:00', '2023-12-29 11:30:00', 'RETURNED', 0),
(5, 84, 'BORROW', '2023-12-08 11:50:00', '2024-01-07 11:50:00', '2024-01-05 14:20:00', 'RETURNED', 0),
(6, 95, 'BORROW', '2023-12-12 16:30:00', '2024-01-11 16:30:00', '2024-01-08 10:45:00', 'RETURNED', 0),

-- Older transaction history (September - October 2023) - 30 transactions
(7, 5, 'BORROW', '2023-09-10 09:15:00', '2023-10-10 09:15:00', '2023-10-08 14:30:00', 'RETURNED', 0),
(8, 20, 'BORROW', '2023-09-15 13:45:00', '2023-10-15 13:45:00', '2023-10-18 11:20:00', 'RETURNED', 30),
(9, 35, 'BORROW', '2023-09-20 11:30:00', '2023-10-20 11:30:00', '2023-10-15 16:45:00', 'RETURNED', 0),
(10, 50, 'BORROW', '2023-09-25 15:20:00', '2023-10-25 15:20:00', '2023-10-28 09:10:00', 'RETURNED', 30),
(11, 65, 'BORROW', '2023-09-30 10:40:00', '2023-10-30 10:40:00', '2023-10-25 13:55:00', 'RETURNED', 0),
(12, 76, 'BORROW', '2023-10-05 14:25:00', '2023-11-04 14:25:00', '2023-11-02 12:15:00', 'RETURNED', 0),
(13, 87, 'BORROW', '2023-10-10 12:50:00', '2023-11-09 12:50:00', '2023-11-12 15:30:00', 'RETURNED', 30),
(14, 92, 'BORROW', '2023-10-15 16:35:00', '2023-11-14 16:35:00', '2023-11-10 10:20:00', 'RETURNED', 0),
(15, 6, 'BORROW', '2023-09-12 11:20:00', '2023-10-12 11:20:00', '2023-10-09 14:45:00', 'RETURNED', 0),
(16, 21, 'BORROW', '2023-09-18 14:55:00', '2023-10-18 14:55:00', '2023-10-21 16:30:00', 'RETURNED', 30),
(17, 36, 'BORROW', '2023-09-22 10:10:00', '2023-10-22 10:10:00', '2023-10-19 12:25:00', 'RETURNED', 0),
(18, 51, 'BORROW', '2023-09-28 13:30:00', '2023-10-28 13:30:00', '2023-10-31 15:40:00', 'RETURNED', 30),
(19, 66, 'BORROW', '2023-10-02 15:45:00', '2023-11-01 15:45:00', '2023-10-28 11:15:00', 'RETURNED', 0),
(20, 77, 'BORROW', '2023-10-08 12:15:00', '2023-11-07 12:15:00', '2023-11-05 14:50:00', 'RETURNED', 0),
(21, 88, 'BORROW', '2023-10-12 16:40:00', '2023-11-11 16:40:00', '2023-11-14 10:25:00', 'RETURNED', 30),
(22, 93, 'BORROW', '2023-10-18 11:55:00', '2023-11-17 11:55:00', '2023-11-13 13:20:00', 'RETURNED', 0),
(23, 7, 'BORROW', '2023-09-14 13:25:00', '2023-10-14 13:25:00', '2023-10-11 15:35:00', 'RETURNED', 0),
(24, 22, 'BORROW', '2023-09-20 15:50:00', '2023-10-20 15:50:00', '2023-10-23 12:10:00', 'RETURNED', 30),
(25, 37, 'BORROW', '2023-09-26 10:35:00', '2023-10-26 10:35:00', '2023-10-22 14:45:00', 'RETURNED', 0),
(26, 52, 'BORROW', '2023-10-01 14:20:00', '2023-10-31 14:20:00', '2023-11-03 16:55:00', 'RETURNED', 30),
(27, 67, 'BORROW', '2023-10-06 12:45:00', '2023-11-05 12:45:00', '2023-11-01 11:30:00', 'RETURNED', 0),
(28, 78, 'BORROW', '2023-10-11 16:10:00', '2023-11-10 16:10:00', '2023-11-08 13:25:00', 'RETURNED', 0),
(29, 89, 'BORROW', '2023-10-16 11:40:00', '2023-11-15 11:40:00', '2023-11-18 15:15:00', 'RETURNED', 30),
(30, 94, 'BORROW', '2023-10-22 13:55:00', '2023-11-21 13:55:00', '2023-11-17 10:40:00', 'RETURNED', 0),
(31, 8, 'BORROW', '2023-09-16 15:30:00', '2023-10-16 15:30:00', '2023-10-13 12:20:00', 'RETURNED', 0),
(32, 23, 'BORROW', '2023-09-24 12:05:00', '2023-10-24 12:05:00', '2023-10-27 14:35:00', 'RETURNED', 30),
(33, 38, 'BORROW', '2023-09-29 14:40:00', '2023-10-29 14:40:00', '2023-10-25 16:50:00', 'RETURNED', 0),
(4, 53, 'BORROW', '2023-10-03 16:25:00', '2023-11-02 16:25:00', '2023-10-30 11:15:00', 'RETURNED', 0),
(5, 68, 'BORROW', '2023-10-09 11:50:00', '2023-11-08 11:50:00', '2023-11-06 13:40:00', 'RETURNED', 0),
(6, 79, 'BORROW', '2023-10-14 13:15:00', '2023-11-13 13:15:00', '2023-11-16 15:25:00', 'RETURNED', 30),

-- Summer 2023 transactions (July - August) - 22 transactions
(7, 9, 'BORROW', '2023-07-15 10:20:00', '2023-08-14 10:20:00', '2023-08-12 14:35:00', 'RETURNED', 0),
(8, 24, 'BORROW', '2023-07-20 14:45:00', '2023-08-19 14:45:00', '2023-08-22 16:20:00', 'RETURNED', 30),
(9, 39, 'BORROW', '2023-07-25 12:30:00', '2023-08-24 12:30:00', '2023-08-20 11:45:00', 'RETURNED', 0),
(10, 54, 'BORROW', '2023-07-30 16:15:00', '2023-08-29 16:15:00', '2023-09-01 13:25:00', 'RETURNED', 30),
(11, 69, 'BORROW', '2023-08-05 11:40:00', '2023-09-04 11:40:00', '2023-09-02 15:10:00', 'RETURNED', 0),
(12, 80, 'BORROW', '2023-08-10 15:25:00', '2023-09-09 15:25:00', '2023-09-07 12:50:00', 'RETURNED', 0),
(13, 91, 'BORROW', '2023-08-15 13:50:00', '2023-09-14 13:50:00', '2023-09-17 16:35:00', 'RETURNED', 30),
(14, 10, 'BORROW', '2023-07-18 12:10:00', '2023-08-17 12:10:00', '2023-08-15 10:25:00', 'RETURNED', 0),
(15, 25, 'BORROW', '2023-07-22 16:35:00', '2023-08-21 16:35:00', '2023-08-24 14:40:00', 'RETURNED', 30),
(16, 40, 'BORROW', '2023-07-28 11:55:00', '2023-08-27 11:55:00', '2023-08-25 13:15:00', 'RETURNED', 0),
(17, 55, 'BORROW', '2023-08-02 14:20:00', '2023-09-01 14:20:00', '2023-08-30 16:45:00', 'RETURNED', 0),
(18, 70, 'BORROW', '2023-08-08 10:45:00', '2023-09-07 10:45:00', '2023-09-05 12:30:00', 'RETURNED', 0),
(19, 81, 'BORROW', '2023-08-12 13:30:00', '2023-09-11 13:30:00', '2023-09-14 15:55:00', 'RETURNED', 30),
(20, 92, 'BORROW', '2023-08-18 15:55:00', '2023-09-17 15:55:00', '2023-09-15 11:20:00', 'RETURNED', 0),
(21, 11, 'BORROW', '2023-07-20 11:25:00', '2023-08-19 11:25:00', '2023-08-17 14:50:00', 'RETURNED', 0),
(22, 26, 'BORROW', '2023-07-26 15:40:00', '2023-08-25 15:40:00', '2023-08-28 12:15:00', 'RETURNED', 30),
(23, 41, 'BORROW', '2023-08-01 12:15:00', '2023-08-31 12:15:00', '2023-08-29 16:30:00', 'RETURNED', 0),
(24, 56, 'BORROW', '2023-08-06 16:50:00', '2023-09-05 16:50:00', '2023-09-03 11:40:00', 'RETURNED', 0),
(25, 71, 'BORROW', '2023-08-11 11:15:00', '2023-09-10 11:15:00', '2023-09-08 14:25:00', 'RETURNED', 0),
(26, 82, 'BORROW', '2023-08-16 14:40:00', '2023-09-15 14:40:00', '2023-09-18 16:10:00', 'RETURNED', 30),
(27, 93, 'BORROW', '2023-08-22 13:05:00', '2023-09-21 13:05:00', '2023-09-19 15:35:00', 'RETURNED', 0),
(28, 12, 'BORROW', '2023-07-24 10:30:00', '2023-08-23 10:30:00', '2023-08-21 12:45:00', 'RETURNED', 0);

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