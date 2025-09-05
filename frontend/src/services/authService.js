import axios from 'axios';
import { API_CONFIG } from '../config/api';
import { csrfService } from './csrfService';

export const authService = {
  async login(credentials) {
    await csrfService.fetchToken();
    const response = await axios.post(API_CONFIG.getVersionedUrl('/login'), credentials);
    return response.data;
  },

  async logout() {
    try {
      await axios.post(API_CONFIG.getVersionedUrl('/logout'));
    } finally {
      csrfService.clearToken();
    }
  }
};