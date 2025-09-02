import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const bookRequestService = {
  async getRequests() {
    const response = await axios.get(API_CONFIG.getVersionedUrl('/admin/book-requests'));
    return response.data;
  },

  async approveRequest(requestId) {
    const response = await axios.post(API_CONFIG.getVersionedUrl(`/admin/book-requests/${requestId}/approve`));
    return response.data;
  },

  async rejectRequest(requestId, notes = '') {
    const response = await axios.post(API_CONFIG.getVersionedUrl(`/admin/book-requests/${requestId}/reject`), { notes });
    return response.data;
  }
};