import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Edit, Trash2, Eye, Book, X, UserPlus, UserMinus } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchBooks, createBook, updateBook, deleteBook } from '../../store/slices/booksSlice';
import { showNotification } from '../../store/slices/uiSlice';
import ConfirmModal from '../common/ConfirmModal';
import { API_CONFIG } from '../../config/api';
import '../../styles/BookCatalog.css';
import '../../styles/AdminBooks.css';
import '../../styles/BooksTable.css';
import '../../styles/Modal.css';

const BooksManagement = () => {
  const dispatch = useDispatch();
  const { data: books, loading, genres, borrowCounts: bookBorrowCounts } = useSelector(state => state.books);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
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

  const [confirmModal, setConfirmModal] = useState({ isOpen: false, bookId: null, bookTitle: '' });
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    genre: '',
    published_year: '',
    available_copies: ''
  });

  const loadBooks = (query = '') => {
    dispatch(fetchBooks(query));
  };

  // Fetch users for issue modal
  const fetchUsers = async () => {
    try {
      const response = await fetch(API_CONFIG.getVersionedUrl('/admin/users'));
      const data = await response.json();
      setUsers(data.filter(user => user.is_active && user.role === 'USER'));
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // Fetch borrowed transactions for return modal
  const fetchBorrowedTransactions = async (bookId) => {
    try {
      const response = await fetch(API_CONFIG.getVersionedUrl('/admin/transactions?status=BORROWED'));
      const data = await response.json();
      const bookTransactions = data.transactions.filter(txn => txn.book_id === bookId);
      setBorrowedTransactions(bookTransactions);
    } catch (error) {
      console.error('Error fetching borrowed transactions:', error);
    }
  };

  useEffect(() => {
    loadBooks();
  }, [dispatch]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadBooks(searchQuery);
  };

  // Filter books by genre
  const filteredBooks = selectedGenre 
    ? books.filter(book => book.genre === selectedGenre)
    : books;

  const handleSaveBook = async (e) => {
    e.preventDefault();
    try {
      if (editingBook) {
        await dispatch(updateBook({ bookId: editingBook.book_id, bookData: formData })).unwrap();
        dispatch(showNotification({ message: 'Book updated successfully', type: 'success' }));
      } else {
        await dispatch(createBook(formData)).unwrap();
        dispatch(showNotification({ message: 'Book created successfully', type: 'success' }));
      }
      handleCloseModal();
      loadBooks();
    } catch (error) {
      dispatch(showNotification({ message: 'Failed to save book', type: 'error' }));
    }
  };

  // Handle delete book
  const handleDeleteBook = (book) => {
    setConfirmModal({
      isOpen: true,
      bookId: book.book_id,
      bookTitle: book.title,
      message: `Are you sure you want to delete "${book.title}"? This action cannot be undone.`
    });
  };

  const confirmDeleteBook = async () => {
    try {
      await dispatch(deleteBook(confirmModal.bookId)).unwrap();
      dispatch(showNotification({ message: 'Book deleted successfully', type: 'success' }));
    } catch (error) {
      dispatch(showNotification({ message: 'Failed to delete book', type: 'error' }));
    }
    setConfirmModal({ isOpen: false, bookId: null, bookTitle: '' });
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
      const response = await fetch(API_CONFIG.getVersionedUrl('/admin/issue-book'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: issuingBook.book_id,
          user_id: selectedUser.user_id
        })
      });
      
      if (response.ok) {
        loadBooks();
        handleCloseIssueModal();
        dispatch(showNotification({ message: 'Book issued successfully', type: 'success' }));
      } else {
        dispatch(showNotification({ message: 'Failed to issue book', type: 'error' }));
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
      const response = await fetch(API_CONFIG.getVersionedUrl('/admin/return-book'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transaction_id: selectedTransaction.transaction_id
        })
      });
      
      if (response.ok) {
        loadBooks();
        handleCloseReturnModal();
        dispatch(showNotification({ message: 'Book returned successfully', type: 'success' }));
      } else {
        dispatch(showNotification({ message: 'Failed to return book', type: 'error' }));
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
                        <button className="action-btn delete" title="Delete" onClick={() => handleDeleteBook(book)}>
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
                loadBooks();
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

      <ConfirmModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ isOpen: false, bookId: null, bookTitle: '' })}
        onConfirm={confirmDeleteBook}
        title="Delete Book"
        message={confirmModal.message}
        confirmText="Delete"
        type="danger"
      />
    </div>
  );
};

export default BooksManagement;