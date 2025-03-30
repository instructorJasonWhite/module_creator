import axios from 'axios';
import { logger, LogCategory } from './utils/logger';

const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
logger.debug(LogCategory.AUTH, `API URL configured: ${apiUrl}`, null, 'Config');

export const config = {
  api: {
    baseUrl: apiUrl,
    endpoints: {
      auth: {
        login: '/api/v1/auth/login',
        verify: '/api/v1/auth/verify',
      },
      documents: {
        upload: '/api/v1/documents/upload',
        outline: '/api/v1/documents/outline',
      },
      agents: {
        analyze: '/api/v1/agents/analyze',
      },
    },
  },
  upload: {
    maxFileSize: 50 * 1024 * 1024, // 50MB in bytes
  },
};

// Create axios instance with default config
export const api = axios.create({
  baseURL: config.api.baseUrl,
  withCredentials: true,
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    logger.error(LogCategory.API, 'API request failed', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
    }, 'Config');
    return Promise.reject(error);
  }
);
