import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { bookService } from '../../services/bookService';

export const fetchBooks = createAsyncThunk(
  'books/fetchBooks',
  async () => {
    const response = await bookService.getBooks();
    return response;
  }
);

const booksSlice = createSlice({
  name: 'books',
  initialState: {
    data: [],
    loading: false,
    error: null,
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
        state.data = action.payload;
      })
      .addCase(fetchBooks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export default booksSlice.reducer;