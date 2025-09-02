import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_CONFIG } from '../../config/api';

const BookSearch = ({ user }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const searchBooks = async () => {
    setLoading(true);
    try {
      const response = await axios.get(API_CONFIG.getVersionedUrl(`/user/books/search?q=${searchQuery}`));
      setBooks(response.data);
    } catch (error) {
      setMessage('Error searching books');
    } finally {
      setLoading(false);
    }
  };

  const requestBook = async (bookId) => {
    try {
      const response = await axios.post(API_CONFIG.getVersionedUrl('/user/book-request'), {
        book_id: bookId,
        request_type: 'ISSUE'
      });
      setMessage(response.data.message);
      searchBooks(); // Refresh the list
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Error requesting book');
    }
  };

  useEffect(() => {
    searchBooks();
  }, []);

  return (
    <div className="book-search">
      <h2>Search Books</h2>
      
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by title, author, or genre..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && searchBooks()}
        />
        <button onClick={searchBooks} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {message && <div className="message">{message}</div>}

      <div className="books-grid">
        {books.map(book => (
          <div key={book.book_id} className="book-card">
            <h3>{book.title}</h3>
            <p><strong>Author:</strong> {book.author}</p>
            <p><strong>Genre:</strong> {book.genre}</p>
            <p><strong>Year:</strong> {book.published_year}</p>
            <p><strong>Available:</strong> {book.available_copies} copies</p>
            
            <button 
              onClick={() => requestBook(book.book_id)}
              disabled={!book.can_request}
              className={book.can_request ? 'btn-primary' : 'btn-disabled'}
            >
              {book.can_request ? 'Request Issue' : 'Not Available'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BookSearch;