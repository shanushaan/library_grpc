// Environment configuration
const getEnvironmentConfig = () => {
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  return {
    API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8001',
    WS_BASE_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8001',
    ENVIRONMENT: process.env.NODE_ENV || 'development',
    IS_DEVELOPMENT: isDevelopment,
    
    // Demo credentials (only for development)
    DEMO_CREDENTIALS: isDevelopment ? {
      admin: { username: 'admin', password: 'admin123' },
      user: { username: 'john_user', password: 'user123' }
    } : null
  };
};

export const ENV_CONFIG = getEnvironmentConfig();