import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const userService = {
  async getUsers() {
    const response = await axios.get(API_CONFIG.getVersionedUrl('/admin/users'));
    return response.data;
  },

  async createUser(userData) {
    const response = await axios.post(API_CONFIG.getVersionedUrl('/admin/users'), userData);
    return response.data;
  },

  async updateUser(userId, userData) {
    const response = await axios.put(API_CONFIG.getVersionedUrl(`/admin/users/${userId}`), userData);
    return response.data;
  },

  async deleteUser(userId) {
    const response = await axios.delete(API_CONFIG.getVersionedUrl(`/admin/users/${userId}`));
    return response.data;
  },

  async toggleUserStatus(userId) {
    const response = await axios.patch(API_CONFIG.getVersionedUrl(`/admin/users/${userId}/toggle-status`));
    return response.data;
  }
};