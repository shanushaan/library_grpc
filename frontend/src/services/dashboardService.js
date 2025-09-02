import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const dashboardService = {
  async getStats() {
    const [booksResponse, usersResponse, statsResponse] = await Promise.all([
      axios.get(API_CONFIG.getVersionedUrl('/admin/books')),
      axios.get(API_CONFIG.getVersionedUrl('/admin/users')),
      axios.get(API_CONFIG.getVersionedUrl('/admin/stats'))
    ]);
    
    return {
      totalBooks: Array.isArray(booksResponse.data) ? booksResponse.data.length : 0,
      activeUsers: Array.isArray(usersResponse.data) ? usersResponse.data.filter(u => u.is_active).length : 0,
      borrowedBooks: statsResponse.data.borrowed_books || 0,
      overdueBooks: statsResponse.data.overdue_books || 0
    };
  }
};