import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const transactionService = {
  async getTransactions() {
    const response = await axios.get(API_CONFIG.getVersionedUrl('/admin/transactions'));
    return response.data;
  },

  async issueBook(userId, bookId) {
    const response = await axios.post(API_CONFIG.getVersionedUrl('/admin/transactions/issue'), {
      user_id: userId,
      book_id: bookId
    });
    return response.data;
  },

  async returnBook(transactionId) {
    const response = await axios.post(API_CONFIG.getVersionedUrl(`/admin/transactions/${transactionId}/return`));
    return response.data;
  },

  async getUserTransactions(userId) {
    const response = await axios.get(API_CONFIG.getVersionedUrl(`/user/${userId}/transactions`));
    return response.data;
  }
};