import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const authService = {
  async login(credentials) {
    const response = await axios.post(API_CONFIG.getVersionedUrl('/login'), credentials);
    return response.data;
  }
};