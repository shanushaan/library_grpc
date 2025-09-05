import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const adminService = {
  async fetchUsers() {
    const response = await axios.get(API_CONFIG.getVersionedUrl('/admin/users'));
    return response.data.filter(user => user.is_active && user.role === 'USER');
  },

  async fetchBorrowedTransactions(bookId) {
    const response = await axios.get(API_CONFIG.getVersionedUrl('/admin/transactions?status=BORROWED'));
    return response.data.transactions.filter(txn => txn.book_id === bookId);
  },

  async issueBook(bookId, userId) {
    const response = await axios.post(API_CONFIG.getVersionedUrl('/admin/issue-book'), {
      book_id: bookId, 
      user_id: userId 
    });
    return response.status === 200;
  },

  async returnBook(transactionId) {
    const response = await axios.post(API_CONFIG.getVersionedUrl('/admin/return-book'), {
      transaction_id: transactionId
    });
    return response.status === 200;
  }
};