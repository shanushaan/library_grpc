import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Book, X, UserPlus, UserMinus } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchBooks, createBook, updateBook, deleteBook } from '../../store/slices/booksSlice';
import { showNotification } from '../../store/slices/uiSlice';
import ConfirmModal from '../common/ConfirmModal';
import EnhancedDataTable from '../common/EnhancedDataTable';
import axios from 'axios';
import { API_CONFIG } from '../../config/api';
import '../../styles/BookCatalog.css';
import '../../styles/AdminBooks.css';
import '../../styles/BooksTable.css';
import '../../styles/Modal.css';

const BooksManagement = () => {
  const dispatch = useDispatch();
  const { data: books, loading, genres, borrowCounts: bookBorrowCounts } = useSelector(state => state.books);
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
      const response = await axios.get(API_CONFIG.getVersionedUrl('/admin/users'));
      setUsers(response.data.filter(user => user.is_active && user.role === 'USER'));
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // Fetch borrowed transactions for return modal
  const fetchBorrowedTransactions = async (bookId) => {
    try {
      const response = await axios.get(API_CONFIG.getVersionedUrl('/admin/transactions?status=BORROWED'));
      const bookTransactions = response.data.transactions.filter(txn => txn.book_id === bookId);
      setBorrowedTransactions(bookTransactions);
    } catch (error) {
      console.error('Error fetching borrowed transactions:', error);
    }
  };

  useEffect(() => {
    loadBooks();
  }, [dispatch]);



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
      await axios.post(API_CONFIG.getVersionedUrl('/admin/issue-book'), {
        book_id: issuingBook.book_id,
        user_id: selectedUser.user_id
      });
      
      loadBooks();
      handleCloseIssueModal();
      dispatch(showNotification({ message: 'Book issued successfully', type: 'success' }));
    } catch (error) {
      console.error('Error issuing book:', error);
      dispatch(showNotification({ message: 'Failed to issue book', type: 'error' }));
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
      await axios.post(API_CONFIG.getVersionedUrl('/admin/return-book'), {
        transaction_id: selectedTransaction.transaction_id
      });
      
      loadBooks();
      handleCloseReturnModal();
      dispatch(showNotification({ message: 'Book returned successfully', type: 'success' }));
    } catch (error) {
      console.error('Error returning book:', error);
      dispatch(showNotification({ message: 'Failed to return book', type: 'error' }));
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

      <EnhancedDataTable
        data={books}
        columns={[
          { key: 'title', header: 'Title', render: (value) => <span className="book-title-cell">{value}</span> },
          { key: 'author', header: 'Author', render: (value) => value || 'Unknown' },
          { key: 'genre', header: 'Genre', render: (value) => <span className="genre-tag">{value || 'Unknown'}</span> },
          { key: 'published_year', header: 'Year', render: (value) => value || 'N/A' },
          { key: 'available_copies', header: 'Available', render: (value) => (
            <span className={`availability-badge ${value > 0 ? 'available' : 'unavailable'}`}>
              {value}
            </span>
          )},
          { key: 'actions', header: 'Actions', render: (_, book) => (
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
          )}
        ]}
        keyField="book_id"
        searchable={true}
        searchPlaceholder="Search by title, author, or genre..."
        filters={[
          ...genres.map(genre => ({
            value: genre,
            label: genre,
            filter: (book) => book.genre === genre
          }))
        ]}
        emptyMessage={loading ? "Loading books..." : "No books found"}
        className="books-table"
      />

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