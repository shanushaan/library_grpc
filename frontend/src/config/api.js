import axios from 'axios';
import { ENV_CONFIG } from './environment';
import { csrfService } from '../services/csrfService';

export const API_CONFIG = {
  BASE_URL: ENV_CONFIG.API_BASE_URL,
  VERSION: 'v1',
  getVersionedUrl: (endpoint) => `${API_CONFIG.BASE_URL}/api/${API_CONFIG.VERSION}${endpoint}`
};

// Configure axios interceptors for CSRF protection
axios.interceptors.request.use(
  (config) => {
    const token = csrfService.getToken();
    if (token && ['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase())) {
      config.headers['X-CSRF-Token'] = token;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403 && error.response?.data?.error === 'CSRF token mismatch') {
      csrfService.clearToken();
      csrfService.fetchToken();
    }
    return Promise.reject(error);
  }
);}