import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { bookRequestService } from '../../services/bookRequestService';

export const fetchBookRequests = createAsyncThunk(
  'bookRequests/fetchBookRequests',
  async () => {
    const response = await bookRequestService.getRequests();
    return response;
  }
);

export const approveBookRequest = createAsyncThunk(
  'bookRequests/approveBookRequest',
  async (requestId) => {
    const response = await bookRequestService.approveRequest(requestId);
    return { requestId, message: response.message };
  }
);

export const rejectBookRequest = createAsyncThunk(
  'bookRequests/rejectBookRequest',
  async ({ requestId, notes }) => {
    const response = await bookRequestService.rejectRequest(requestId, notes);
    return { requestId, message: response.message };
  }
);

const bookRequestsSlice = createSlice({
  name: 'bookRequests',
  initialState: {
    data: [],
    loading: false,
    error: null,
    pendingCount: 0,
  },
  reducers: {
    incrementPendingCount: (state) => {
      state.pendingCount += 1;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBookRequests.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBookRequests.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
        state.pendingCount = action.payload.filter(req => req.status === 'PENDING').length;
      })
      .addCase(fetchBookRequests.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(approveBookRequest.fulfilled, (state, action) => {
        state.data = state.data.filter(req => req.request_id !== action.payload.requestId);
        state.pendingCount = Math.max(0, state.pendingCount - 1);
      })
      .addCase(rejectBookRequest.fulfilled, (state, action) => {
        state.data = state.data.filter(req => req.request_id !== action.payload.requestId);
        state.pendingCount = Math.max(0, state.pendingCount - 1);
      });
  },
});

export const { incrementPendingCount } = bookRequestsSlice.actions;
export default bookRequestsSlice.reducer;