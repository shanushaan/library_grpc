import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import axios from 'axios';
import { API_CONFIG } from '../../config/api';
import { showNotification } from '../../store/slices/uiSlice';
import { transactionValidation } from '../../utils/validationSchemas';
import { handleApiError } from '../../utils/errorHandler';
import ErrorBoundary from '../common/ErrorBoundary';
import DataTable from '../common/DataTable';

const BookSearch = ({ user }) => {
  const dispatch = useDispatch();
  const [searchQuery, setSearchQuery] = useState('');
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userTransactions, setUserTransactions] = useState([]);

  const searchBooks = async () => {
    setLoading(true);
    try {
      const response = await axios.get(API_CONFIG.getVersionedUrl(`/user/books/search?q=${searchQuery}`));
      setBooks(response.data);
    } catch (error) {
      handleApiError(error, dispatch, showNotification);
    } finally {
      setLoading(false);
    }
  };

  const requestBook = async (bookId) => {
    // Validate transaction before making request
    const book = books.find(b => b.book_id === bookId);
    
    const availabilityError = transactionValidation.validateBookAvailability(book, 'ISSUE');
    if (availabilityError) {
      dispatch(showNotification({ message: availabilityError, type: 'error' }));
      return;
    }
    
    const duplicateError = transactionValidation.validateDuplicateIssue(userTransactions, bookId);
    if (duplicateError) {
      dispatch(showNotification({ message: duplicateError, type: 'error' }));
      return;
    }
    
    const limitError = transactionValidation.validateUserLimit(userTransactions);
    if (limitError) {
      dispatch(showNotification({ message: limitError, type: 'error' }));
      return;
    }
    
    try {
      const response = await axios.post(API_CONFIG.getVersionedUrl('/user/book-request'), {
        book_id: bookId,
        request_type: 'ISSUE',
        user_id: user.user_id,
        notes: 'Book request from search'
      });
      dispatch(showNotification({ message: response.data.message, type: 'success' }));
      searchBooks();
      fetchUserTransactions();
    } catch (error) {
      handleApiError(error, dispatch, showNotification);
    }
  };

  const fetchUserTransactions = async () => {
    try {
      const response = await axios.get(API_CONFIG.getVersionedUrl(`/user/${user.user_id}/transactions`));
      setUserTransactions(response.data);
    } catch (error) {
      handleApiError(error, dispatch, showNotification);
    }
  };
  
  useEffect(() => {
    searchBooks();
    fetchUserTransactions();
  }, []);

  return (
    <ErrorBoundary fallbackMessage="Book search unavailable.">
      <div className="page-content">
        <div className="page-header">
          <h2>Search Books</h2>
          <p>Search and request books from our collection</p>
        </div>
        
        <div className="search-section">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search by title, author, or genre..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchBooks()}
              className="search-input"
            />
            <button onClick={searchBooks} disabled={loading} className="search-button">
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Searching books...</p>
          </div>
        ) : (
          <DataTable
            data={books}
            columns={[
              { key: 'title', header: 'Title' },
              { key: 'author', header: 'Author', render: (value) => value || 'Unknown' },
              { key: 'genre', header: 'Genre', render: (value) => value || 'Unknown' },
              { key: 'published_year', header: 'Year', render: (value) => value || 'N/A' },
              { 
                key: 'available_copies', 
                header: 'Available',
                render: (value) => `${value} copies`
              },
              {
                key: 'actions',
                header: 'Action',
                render: (_, book) => (
                  <button 
                    onClick={() => requestBook(book.book_id)}
                    disabled={!book.can_request}
                    className={book.can_request ? 'btn btn-primary' : 'btn btn-disabled'}
                  >
                    {book.can_request ? 'Request' : 'Not Available'}
                  </button>
                )
              }
            ]}
            keyField="book_id"
            emptyMessage="No books found. Try a different search term."
            className="books-search-table"
          />
        )}
      </div>
    </ErrorBoundary>
  );
};

export default BookSearch;