import { configureStore } from '@reduxjs/toolkit';
import bookRequestsSlice from './slices/bookRequestsSlice';
import usersSlice from './slices/usersSlice';
import booksSlice from './slices/booksSlice';
import transactionsSlice from './slices/transactionsSlice';
import uiSlice from './slices/uiSlice';
import { persistenceMiddleware, loadPersistedState } from './middleware/persistenceMiddleware';

const preloadedState = loadPersistedState();

export const store = configureStore({
  reducer: {
    bookRequests: bookRequestsSlice,
    users: usersSlice,
    books: booksSlice,
    transactions: transactionsSlice,
    ui: uiSlice,
  },
  preloadedState,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(persistenceMiddleware),
  devTools: process.env.NODE_ENV !== 'production',
});

export const selectBookRequests = (state) => state.bookRequests;
export const selectUsers = (state) => state.users;
export const selectBooks = (state) => state.books;
export const selectTransactions = (state) => state.transactions;
export const selectUI = (state) => state.ui;