import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { userService } from '../../services/userService';

export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async () => {
    const response = await userService.getUsers();
    return response;
  }
);

export const createUser = createAsyncThunk(
  'users/createUser',
  async (userData) => {
    const response = await userService.createUser(userData);
    return response;
  }
);

export const updateUser = createAsyncThunk(
  'users/updateUser',
  async ({ userId, userData }) => {
    const response = await userService.updateUser(userId, userData);
    return { userId, userData };
  }
);

export const toggleUserStatus = createAsyncThunk(
  'users/toggleUserStatus',
  async (userId) => {
    await userService.toggleUserStatus(userId);
    return userId;
  }
);

const usersSlice = createSlice({
  name: 'users',
  initialState: {
    data: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(createUser.fulfilled, (state) => {
        // Refetch will be triggered
      })
      .addCase(updateUser.fulfilled, (state) => {
        // Refetch will be triggered
      })
      .addCase(toggleUserStatus.fulfilled, (state, action) => {
        const user = state.data.find(u => u.user_id === action.payload);
        if (user) {
          user.is_active = !user.is_active;
        }
      });
  },
});

export default usersSlice.reducer;