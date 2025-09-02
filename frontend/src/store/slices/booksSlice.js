import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { API_CONFIG } from '../../config/api';

export const fetchBooks = createAsyncThunk(
  'books/fetchBooks',
  async (query = '') => {
    const [booksResponse, transactionsResponse] = await Promise.all([
      fetch(API_CONFIG.getVersionedUrl(`/admin/books?q=${encodeURIComponent(query)}`)),
      fetch(API_CONFIG.getVersionedUrl('/admin/transactions?status=BORROWED'))
    ]);
    
    const booksData = await booksResponse.json();
    const transactionsData = await transactionsResponse.json();
    
    // Count borrowed books per book_id
    const borrowCounts = {};
    transactionsData.transactions.forEach(txn => {
      borrowCounts[txn.book_id] = (borrowCounts[txn.book_id] || 0) + 1;
    });
    
    return { books: booksData, borrowCounts };
  }
);

export const createBook = createAsyncThunk(
  'books/createBook',
  async (bookData) => {
    const response = await fetch(API_CONFIG.getVersionedUrl('/admin/books'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...bookData,
        published_year: parseInt(bookData.published_year) || null,
        available_copies: parseInt(bookData.available_copies) || 0
      })
    });
    
    if (!response.ok) throw new Error('Failed to create book');
    return await response.json();
  }
);

export const updateBook = createAsyncThunk(
  'books/updateBook',
  async ({ bookId, bookData }) => {
    const response = await fetch(API_CONFIG.getVersionedUrl(`/admin/books/${bookId}`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...bookData,
        published_year: parseInt(bookData.published_year) || null,
        available_copies: parseInt(bookData.available_copies) || 0
      })
    });
    
    if (!response.ok) throw new Error('Failed to update book');
    return { bookId, ...bookData };
  }
);

export const deleteBook = createAsyncThunk(
  'books/deleteBook',
  async (bookId) => {
    const response = await fetch(API_CONFIG.getVersionedUrl(`/admin/books/${bookId}`), {
      method: 'DELETE'
    });
    
    if (!response.ok) throw new Error('Failed to delete book');
    return bookId;
  }
);

const booksSlice = createSlice({
  name: 'books',
  initialState: {
    data: [],
    loading: false,
    error: null,
    genres: [],
    borrowCounts: {},
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchBooks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBooks.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload.books;
        state.borrowCounts = action.payload.borrowCounts;
        state.genres = [...new Set(action.payload.books.map(book => book.genre).filter(Boolean))];
      })
      .addCase(fetchBooks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(createBook.fulfilled, (state) => {
        // Refetch will be triggered
      })
      .addCase(updateBook.fulfilled, (state) => {
        // Refetch will be triggered
      })
      .addCase(deleteBook.fulfilled, (state, action) => {
        state.data = state.data.filter(book => book.book_id !== action.payload);
      });
  },
});

export default booksSlice.reducer;