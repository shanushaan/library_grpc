import React, { useState, useEffect } from 'react';
import { Search, Book, Filter } from 'lucide-react';
import '../../styles/BookCatalog.css';
import '../../styles/BooksTable.css';

const BookCatalog = ({ user }) => {
  const [books, setBooks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [loading, setLoading] = useState(false);
  const [genres, setGenres] = useState([]);

  // Fetch books from API
  const fetchBooks = async (query = '') => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8001/user/books/search?q=${encodeURIComponent(query)}`);
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

  // Request book function
  const requestBook = async (bookId) => {
    try {
      const response = await fetch('http://localhost:8001/user/book-request', {
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
        alert('Book request submitted successfully!');
      } else {
        alert('Failed to submit book request');
      }
    } catch (error) {
      console.error('Error requesting book:', error);
      alert('Error submitting request');
    }
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Book Catalog</h2>
        <p>Discover and search through our collection of books</p>
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
          <h3>Search Results ({filteredBooks.length} books found)</h3>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Searching books...</p>
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
                  <th>Action</th>
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
                      <button 
                        className={`request-btn ${
                          book.available_copies > 0 ? 'enabled' : 'disabled'
                        }`}
                        onClick={() => requestBook(book.book_id)}
                        disabled={book.available_copies === 0}
                      >
                        {book.available_copies > 0 ? 'Request' : 'Unavailable'}
                      </button>
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
    </div>
  );
};

export default BookCatalog;