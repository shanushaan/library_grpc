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
      const notification = {
        id: Date.now(),
        message: action.payload.message,
        type: action.payload.type || 'info',
        autoHide: action.payload.autoHide !== false,
      };
      state.notifications.push(notification);
      
      // Auto-dismiss after 5 seconds
      if (notification.autoHide) {
        setTimeout(() => {
          // This will be handled by the component
        }, 5000);
      }
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        notification => notification.id !== action.payload
      );
    },
    clearAllNotifications: (state) => {
      state.notifications = [];
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
  clearAllNotifications,
  openRejectModal, 
  closeRejectModal 
} = uiSlice.actions;

export default uiSlice.reducer;