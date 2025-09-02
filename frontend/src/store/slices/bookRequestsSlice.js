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
  },
  reducers: {
    optimisticApprove: (state, action) => {
      state.data = state.data.filter(req => req.request_id !== action.payload);
    },
    optimisticReject: (state, action) => {
      state.data = state.data.filter(req => req.request_id !== action.payload);
    },
    revertOptimistic: (state, action) => {
      // Revert optimistic update on error
      state.data = action.payload;
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
      })
      .addCase(fetchBookRequests.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(approveBookRequest.pending, (state, action) => {
        // Optimistic update already done
      })
      .addCase(approveBookRequest.fulfilled, (state, action) => {
        // Already updated optimistically
      })
      .addCase(approveBookRequest.rejected, (state, action) => {
        // Revert optimistic update
        dispatch(fetchBookRequests());
      })
      .addCase(rejectBookRequest.pending, (state, action) => {
        // Optimistic update already done
      })
      .addCase(rejectBookRequest.fulfilled, (state, action) => {
        // Already updated optimistically
      })
      .addCase(rejectBookRequest.rejected, (state, action) => {
        // Revert optimistic update
        dispatch(fetchBookRequests());
      });
  },
});

export const { optimisticApprove, optimisticReject, revertOptimistic } = bookRequestsSlice.actions;
export default bookRequestsSlice.reducer;