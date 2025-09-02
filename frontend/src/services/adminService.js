import { API_CONFIG } from '../config/api';

export const adminService = {
  async fetchUsers() {
    const response = await fetch(API_CONFIG.getVersionedUrl('/admin/users'));
    const data = await response.json();
    return data.filter(user => user.is_active && user.role === 'USER');
  },

  async fetchBorrowedTransactions(bookId) {
    const response = await fetch(API_CONFIG.getVersionedUrl('/admin/transactions?status=BORROWED'));
    const data = await response.json();
    return data.transactions.filter(txn => txn.book_id === bookId);
  },

  async issueBook(bookId, userId) {
    const response = await fetch(API_CONFIG.getVersionedUrl('/admin/issue-book'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ book_id: bookId, user_id: userId })
    });
    return response.ok;
  },

  async returnBook(transactionId) {
    const response = await fetch(API_CONFIG.getVersionedUrl('/admin/return-book'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transaction_id: transactionId })
    });
    return response.ok;
  }
};