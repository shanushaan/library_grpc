import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Edit, Trash2, Eye, Book, X, UserPlus, UserMinus } from 'lucide-react';
import '../../styles/BookCatalog.css';
import '../../styles/AdminBooks.css';
import '../../styles/BooksTable.css';
import '../../styles/Modal.css';

const BooksManagement = () => {
  const [books, setBooks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [loading, setLoading] = useState(false);
  const [genres, setGenres] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [showReturnModal, setShowReturnModal] = useState(false);
  const [editingBook, setEditingBook] = useState(null);
  const [issuingBook, setIssuingBook] = useState(null);
  const [returningBook, setReturningBook] = useState(null);
  const [users, setUsers] = useState([]);
  const [borrowedTransactions, setBorrowedTransactions] = useState([]);
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [bookBorrowCounts, setBookBorrowCounts] = useState({});
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    genre: '',
    published_year: '',
    available_copies: ''
  });

  // Fetch books from API
  const fetchBooks = async (query = '') => {
    setLoading(true);
    try {
      const [booksResponse, transactionsResponse] = await Promise.all([
        fetch(`http://localhost:8001/admin/books?q=${encodeURIComponent(query)}`),
        fetch('http://localhost:8001/admin/transactions?status=BORROWED')
      ]);
      
      const booksData = await booksResponse.json();
      const transactionsData = await transactionsResponse.json();
      
      setBooks(booksData);
      
      // Extract unique genres
      const uniqueGenres = [...new Set(booksData.map(book => book.genre).filter(Boolean))];
      setGenres(uniqueGenres);
      
      // Count borrowed books per book_id
      const borrowCounts = {};
      transactionsData.transactions.forEach(txn => {
        borrowCounts[txn.book_id] = (borrowCounts[txn.book_id] || 0) + 1;
      });
      setBookBorrowCounts(borrowCounts);
    } catch (error) {
      console.error('Error fetching books:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch users for issue modal
  const fetchUsers = async () => {
    try {
      const response = await fetch('http://localhost:8001/admin/users');
      const data = await response.json();
      setUsers(data.filter(user => user.is_active && user.role === 'USER'));
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // Fetch borrowed transactions for return modal
  const fetchBorrowedTransactions = async (bookId) => {
    try {
      const response = await fetch('http://localhost:8001/admin/transactions?status=BORROWED');
      const data = await response.json();
      const bookTransactions = data.transactions.filter(txn => txn.book_id === bookId);
      setBorrowedTransactions(bookTransactions);
    } catch (error) {
      console.error('Error fetching borrowed transactions:', error);
    }
  };

  // Load books on component mount
  useEffect(() => {
    fetchBooks();
  }, []);

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    fetchBooks(searchQuery);
  };

  // Filter books by genre
  const filteredBooks = selectedGenre 
    ? books.filter(book => book.genre === selectedGenre)
    : books;

  // Handle create/update book
  const handleSaveBook = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const url = editingBook 
        ? `http://localhost:8001/admin/books/${editingBook.book_id}`
        : 'http://localhost:8001/admin/books';
      const method = editingBook ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          published_year: parseInt(formData.published_year) || null,
          available_copies: parseInt(formData.available_copies) || 0
        })
      });
      
      if (response.ok) {
        await fetchBooks();
        handleCloseModal();
      } else {
        console.error('Failed to save book');
      }
    } catch (error) {
      console.error('Error saving book:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle delete book
  const handleDeleteBook = async (bookId) => {
    if (!window.confirm('Are you sure you want to delete this book?')) return;
    
    try {
      const response = await fetch(`http://localhost:8001/admin/books/${bookId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        await fetchBooks();
      } else {
        console.error('Failed to delete book');
      }
    } catch (error) {
      console.error('Error deleting book:', error);
    }
  };

  // Handle edit book
  const handleEditBook = (book) => {
    setEditingBook(book);
    setFormData({
      title: book.title || '',
      author: book.author || '',
      genre: book.genre || '',
      published_year: book.published_year?.toString() || '',
      available_copies: book.available_copies?.toString() || ''
    });
    setShowModal(true);
  };

  // Handle add new book
  const handleAddBook = () => {
    setEditingBook(null);
    setFormData({
      title: '',
      author: '',
      genre: '',
      published_year: '',
      available_copies: ''
    });
    setShowModal(true);
  };

  // Handle close modal
  const handleCloseModal = () => {
    setShowModal(false);
    setEditingBook(null);
    setFormData({
      title: '',
      author: '',
      genre: '',
      published_year: '',
      available_copies: ''
    });
  };

  // Handle issue book
  const handleIssueBook = (book) => {
    setIssuingBook(book);
    setShowIssueModal(true);
    fetchUsers();
  };

  // Handle close issue modal
  const handleCloseIssueModal = () => {
    setShowIssueModal(false);
    setIssuingBook(null);
    setSelectedUser(null);
    setUserSearchQuery('');
  };

  // Handle issue book to user
  const handleConfirmIssue = async () => {
    if (!selectedUser || !issuingBook) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8001/admin/issue-book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: issuingBook.book_id,
          user_id: selectedUser.user_id
        })
      });
      
      if (response.ok) {
        await fetchBooks();
        handleCloseIssueModal();
      } else {
        console.error('Failed to issue book');
      }
    } catch (error) {
      console.error('Error issuing book:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter users based on search
  const filteredUsers = users.filter(user => 
    user.username.toLowerCase().includes(userSearchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(userSearchQuery.toLowerCase())
  );

  // Handle return book
  const handleReturnBook = (book) => {
    setReturningBook(book);
    setShowReturnModal(true);
    fetchBorrowedTransactions(book.book_id);
  };

  // Handle close return modal
  const handleCloseReturnModal = () => {
    setShowReturnModal(false);
    setReturningBook(null);
    setSelectedTransaction(null);
    setBorrowedTransactions([]);
  };

  // Handle confirm return
  const handleConfirmReturn = async () => {
    if (!selectedTransaction) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8001/admin/return-book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transaction_id: selectedTransaction.transaction_id
        })
      });
      
      if (response.ok) {
        await fetchBooks();
        handleCloseReturnModal();
      } else {
        console.error('Failed to return book');
      }
    } catch (error) {
      console.error('Error returning book:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-content books-management">
      <div className="page-header">
        <div className="header-left">
          <h2>Librarian Books Management</h2>
          <p>Manage your library's book collection ({books.length} books)</p>
        </div>
        <div className="header-actions">
          <button className="btn primary" onClick={handleAddBook}>
            <Plus size={20} />
            Add New Book
          </button>
        </div>
      </div>

      {/* Search Section */}
      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-group">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              placeholder="Search by title, author, or genre..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="search-button">
              Search
            </button>
          </div>
        </form>

        {/* Genre Filter */}
        <div className="filter-section">
          <Filter size={16} />
          <select 
            value={selectedGenre} 
            onChange={(e) => setSelectedGenre(e.target.value)}
            className="genre-filter"
          >
            <option value="">All Genres</option>
            {genres.map(genre => (
              <option key={genre} value={genre}>{genre}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Results Section */}
      <div className="results-section">
        <div className="results-header">
          <h3>Book Collection ({filteredBooks.length} books)</h3>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading books...</p>
          </div>
        ) : (
          <div className="books-table-container">
            <table className="books-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Author</th>
                  <th>Genre</th>
                  <th>Year</th>
                  <th>Available</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredBooks.map(book => (
                  <tr key={book.book_id}>
                    <td className="book-title-cell">{book.title}</td>
                    <td>{book.author || 'Unknown'}</td>
                    <td>
                      <span className="genre-tag">{book.genre || 'Unknown'}</span>
                    </td>
                    <td>{book.published_year || 'N/A'}</td>
                    <td>
                      <span className={`availability-badge ${
                        book.available_copies > 0 ? 'available' : 'unavailable'
                      }`}>
                        {book.available_copies}
                      </span>
                    </td>
                    <td>
                      <div className="table-actions">
                        <button 
                          className="action-btn issue" 
                          title="Issue Book" 
                          onClick={() => handleIssueBook(book)}
                          disabled={book.available_copies <= 0}
                        >
                          <UserPlus size={14} />
                        </button>
                        <button 
                          className="action-btn return" 
                          title="Return Book" 
                          onClick={() => handleReturnBook(book)}
                          disabled={!bookBorrowCounts[book.book_id]}
                        >
                          <UserMinus size={14} />
                        </button>
                        <button className="action-btn edit" title="Edit" onClick={() => handleEditBook(book)}>
                          <Edit size={14} />
                        </button>
                        <button className="action-btn delete" title="Delete" onClick={() => handleDeleteBook(book.book_id)}>
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && filteredBooks.length === 0 && (
          <div className="no-results">
            <Book size={48} />
            <h3>No books found</h3>
            <p>Try adjusting your search terms or browse all books</p>
            <button 
              onClick={() => {
                setSearchQuery('');
                setSelectedGenre('');
                fetchBooks();
              }}
              className="reset-button"
            >
              Show All Books
            </button>
          </div>
        )}
      </div>

      {/* Book Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{editingBook ? 'Edit Book' : 'Add New Book'}</h3>
              <button className="close-btn" onClick={handleCloseModal}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSaveBook}>
              <div className="form-group">
                <label>Title *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Author</label>
                <input
                  type="text"
                  value={formData.author}
                  onChange={(e) => setFormData({...formData, author: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Genre</label>
                <input
                  type="text"
                  value={formData.genre}
                  onChange={(e) => setFormData({...formData, genre: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Published Year</label>
                <input
                  type="number"
                  value={formData.published_year}
                  onChange={(e) => setFormData({...formData, published_year: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Available Copies *</label>
                <input
                  type="number"
                  min="0"
                  value={formData.available_copies}
                  onChange={(e) => setFormData({...formData, available_copies: e.target.value})}
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn secondary" onClick={handleCloseModal}>
                  Cancel
                </button>
                <button type="submit" className="btn primary" disabled={loading}>
                  {loading ? 'Saving...' : (editingBook ? 'Update' : 'Create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Issue Book Modal */}
      {showIssueModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Issue Book: {issuingBook?.title}</h3>
              <button className="close-btn" onClick={handleCloseIssueModal}>
                <X size={20} />
              </button>
            </div>
            <div className="issue-modal-body">
              <div className="form-group">
                <label>Search Users</label>
                <input
                  type="text"
                  placeholder="Search by username or email..."
                  value={userSearchQuery}
                  onChange={(e) => setUserSearchQuery(e.target.value)}
                />
              </div>
              <div className="users-list">
                {filteredUsers.map(user => (
                  <div 
                    key={user.user_id} 
                    className={`user-item ${selectedUser?.user_id === user.user_id ? 'selected' : ''}`}
                    onClick={() => setSelectedUser(user)}
                  >
                    <div className="user-info">
                      <strong>{user.username}</strong>
                      <span>{user.email}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="modal-actions">
              <button type="button" className="btn secondary" onClick={handleCloseIssueModal}>
                Cancel
              </button>
              <button 
                type="button" 
                className="btn primary" 
                onClick={handleConfirmIssue}
                disabled={!selectedUser || loading}
              >
                {loading ? 'Issuing...' : 'Issue Book'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Return Book Modal */}
      {showReturnModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Return Book: {returningBook?.title}</h3>
              <button className="close-btn" onClick={handleCloseReturnModal}>
                <X size={20} />
              </button>
            </div>
            <div className="return-modal-body">
              <p>Select the borrower to return the book:</p>
              <div className="borrowers-list">
                {borrowedTransactions.length === 0 ? (
                  <div className="no-borrowers">
                    <p>No active borrowers for this book</p>
                  </div>
                ) : (
                  borrowedTransactions.map(transaction => (
                    <div 
                      key={transaction.transaction_id} 
                      className={`borrower-item ${selectedTransaction?.transaction_id === transaction.transaction_id ? 'selected' : ''}`}
                      onClick={() => setSelectedTransaction(transaction)}
                    >
                      <div className="borrower-info">
                        <strong>{transaction.username}</strong>
                        <span>Borrowed: {new Date(transaction.transaction_date).toLocaleDateString()}</span>
                        <span>Due: {new Date(transaction.due_date).toLocaleDateString()}</span>
                        {transaction.fine_amount > 0 && (
                          <span className="fine-amount">Fine: ₹{transaction.fine_amount}</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
            <div className="modal-actions">
              <button type="button" className="btn secondary" onClick={handleCloseReturnModal}>
                Cancel
              </button>
              <button 
                type="button" 
                className="btn primary" 
                onClick={handleConfirmReturn}
                disabled={!selectedTransaction || loading}
              >
                {loading ? 'Processing...' : 'Return Book'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BooksManagement;