import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { Book, Filter } from 'lucide-react';
import { showNotification } from '../../store/slices/uiSlice';
import { incrementPendingCount } from '../../store/slices/bookRequestsSlice';
import { API_CONFIG } from '../../config/api';
import EnhancedDataTable from '../common/EnhancedDataTable';
import '../../styles/BookCatalog.css';

const BookCatalog = ({ user }) => {
  const dispatch = useDispatch();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [genres, setGenres] = useState([]);

  // Fetch books from API
  const fetchBooks = async (query = '') => {
    setLoading(true);
    try {
      const response = await fetch(API_CONFIG.getVersionedUrl(`/user/books/search?q=${encodeURIComponent(query)}`));
      const data = await response.json();
      setBooks(data);
      
      // Extract unique genres
      const uniqueGenres = [...new Set(data.map(book => book.genre).filter(Boolean))];
      setGenres(uniqueGenres);
    } catch (error) {
      console.error('Error fetching books:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);



  // Request book function
  const requestBook = async (bookId) => {
    try {
      const response = await fetch(API_CONFIG.getVersionedUrl('/user/book-request'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          book_id: bookId,
          request_type: 'ISSUE',
          user_id: user.user_id,
          notes: 'Book request from catalog'
        })
      });
      
      if (response.ok) {
        dispatch(showNotification({ 
          message: 'Book request submitted successfully!', 
          type: 'success' 
        }));
        dispatch(incrementPendingCount());
      } else {
        dispatch(showNotification({ 
          message: 'Failed to submit book request', 
          type: 'error' 
        }));
      }
    } catch (error) {
      console.error('Error requesting book:', error);
      dispatch(showNotification({ 
        message: 'Error submitting request', 
        type: 'error' 
      }));
    }
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Book Catalog</h2>
        <p>Discover and search through our collection of books ({books.length} books)</p>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading books...</p>
        </div>
      ) : (
        <EnhancedDataTable
          data={books}
          columns={[
            { key: 'title', header: 'Title' },
            { key: 'author', header: 'Author', render: (value) => value || 'Unknown' },
            { 
              key: 'genre', 
              header: 'Genre',
              render: (value) => (
                <span className="genre-tag">{value || 'Unknown'}</span>
              )
            },
            { key: 'published_year', header: 'Year', render: (value) => value || 'N/A' },
            { 
              key: 'available_copies', 
              header: 'Available',
              render: (value) => (
                <span className={`availability-badge ${value > 0 ? 'available' : 'unavailable'}`}>
                  {value}
                </span>
              )
            },
            {
              key: 'actions',
              header: 'Action',
              render: (_, book) => (
                <button 
                  className={`request-btn ${book.available_copies > 0 ? 'enabled' : 'disabled'}`}
                  onClick={() => requestBook(book.book_id)}
                  disabled={book.available_copies === 0}
                >
                  {book.available_copies > 0 ? 'Request' : 'Unavailable'}
                </button>
              )
            }
          ]}
          keyField="book_id"
          emptyMessage="No books found"
          className="books-table"
          searchable={true}
          searchPlaceholder="Search by title, author, or genre..."
          filters={genres.map(genre => ({
            value: genre,
            label: genre,
            filter: (book) => book.genre === genre
          }))}
        />
      )}
    </div>
  );
};

export default BookCatalog;