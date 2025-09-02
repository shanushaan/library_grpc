import { createSlice } from '@reduxjs/toolkit';

const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    notifications: [],
    modals: {
      rejectModal: {
        isOpen: false,
        requestId: null,
      },
    },
  },
  reducers: {
    showNotification: (state, action) => {
      state.notifications.push({
        id: Date.now(),
        message: action.payload.message,
        type: action.payload.type || 'info',
      });
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        notification => notification.id !== action.payload
      );
    },
    openRejectModal: (state, action) => {
      state.modals.rejectModal = {
        isOpen: true,
        requestId: action.payload,
      };
    },
    closeRejectModal: (state) => {
      state.modals.rejectModal = {
        isOpen: false,
        requestId: null,
      };
    },
  },
});

export const { 
  showNotification, 
  removeNotification, 
  openRejectModal, 
  closeRejectModal 
} = uiSlice.actions;

export default uiSlice.reducer;