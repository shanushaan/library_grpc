import { ENV_CONFIG } from './environment';

export const API_CONFIG = {
  BASE_URL: ENV_CONFIG.API_BASE_URL,
  VERSION: 'v1',
  getVersionedUrl: (endpoint) => `${API_CONFIG.BASE_URL}/api/${API_CONFIG.VERSION}${endpoint}`
};