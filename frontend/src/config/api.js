export const API_CONFIG = {
  BASE_URL: 'http://localhost:8001',
  VERSION: 'v1',
  getVersionedUrl: (endpoint) => `${API_CONFIG.BASE_URL}/api/${API_CONFIG.VERSION}${endpoint}`
};