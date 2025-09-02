import { configureStore } from '@reduxjs/toolkit';
import bookRequestsSlice from './slices/bookRequestsSlice';
import usersSlice from './slices/usersSlice';
import booksSlice from './slices/booksSlice';
import uiSlice from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    bookRequests: bookRequestsSlice,
    users: usersSlice,
    books: booksSlice,
    ui: uiSlice,
  },
});

export const selectBookRequests = (state) => state.bookRequests;
export const selectUsers = (state) => state.users;
export const selectBooks = (state) => state.books;
export const selectUI = (state) => state.ui;