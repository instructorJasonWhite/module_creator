import axios from 'axios';
import { logger, LogCategory } from './logger';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000',
  withCredentials: true,
  timeout: 300000, // 5 minutes default timeout
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('adminToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Set longer timeout for upload requests
    if (config.data instanceof FormData) {
      config.timeout = 600000; // 10 minutes for uploads
    }
    return config;
  },
  (error) => {
    logger.error(LogCategory.API, 'Request interceptor error', error, 'Axios');
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      logger.error(LogCategory.API, 'Request timed out', {
        message: error.message,
        timeout: error.config?.timeout,
      }, 'Axios');
    } else if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('adminToken');
      window.location.href = '/login';
    }
    logger.error(LogCategory.API, 'API request failed', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
    }, 'Axios');
    return Promise.reject(error);
  }
);

// Add upload progress interceptor
api.interceptors.request.use(
  (config) => {
    if (config.data instanceof FormData) {
      config.onUploadProgress = (progressEvent) => {
        const progress = (progressEvent.loaded / (progressEvent.total || 1)) * 100;
        logger.debug(LogCategory.UPLOAD, `Upload progress: ${Math.round(progress)}%`, null, 'Axios');
      };
    }
    return config;
  },
  (error) => {
    logger.error(LogCategory.API, 'Upload progress interceptor error', error, 'Axios');
    return Promise.reject(error);
  }
);

export default api;
