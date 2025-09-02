import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { API_CONFIG } from '../../config/api';

export const fetchTransactions = createAsyncThunk(
  'transactions/fetchTransactions',
  async ({ status = '', page = 1, limit = 20 }) => {
    const response = await fetch(API_CONFIG.getVersionedUrl(`/admin/transactions?status=${status}&page=${page}&limit=${limit}`));
    const data = await response.json();
    return data;
  }
);

const transactionsSlice = createSlice({
  name: 'transactions',
  initialState: {
    data: [],
    loading: false,
    error: null,
    currentPage: 1,
    totalPages: 1,
    totalCount: 0,
    limit: 20,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchTransactions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTransactions.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload.transactions || [];
        state.currentPage = action.payload.page || 1;
        state.totalPages = action.payload.total_pages || 1;
        state.totalCount = action.payload.total_count || 0;
        state.limit = action.payload.limit || 20;
      })
      .addCase(fetchTransactions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        state.data = [];
      });
  },
});

export default transactionsSlice.reducer;