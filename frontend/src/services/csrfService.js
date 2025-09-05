import axios from 'axios';
import { API_CONFIG } from '../config/api';

class CSRFService {
  constructor() {
    this.token = null;
    this.tokenKey = 'csrf_token';
  }

  generateToken() {
    return Array.from(crypto.getRandomValues(new Uint8Array(32)))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  getToken() {
    if (!this.token) {
      this.token = sessionStorage.getItem(this.tokenKey) || this.generateToken();
      sessionStorage.setItem(this.tokenKey, this.token);
    }
    return this.token;
  }

  async fetchToken() {
    try {
      const response = await axios.get(API_CONFIG.getVersionedUrl('/csrf-token'));
      this.token = response.data.token;
      sessionStorage.setItem(this.tokenKey, this.token);
      return this.token;
    } catch (error) {
      console.warn('Failed to fetch CSRF token from server, using client-generated token');
      return this.getToken();
    }
  }

  clearToken() {
    this.token = null;
    sessionStorage.removeItem(this.tokenKey);
  }

  validateToken(token) {
    return token && token === this.getToken();
  }
}

export const csrfService = new CSRFService();