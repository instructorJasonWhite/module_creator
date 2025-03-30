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
      },
    },
  },
  upload: {
    maxFileSize: 50 * 1024 * 1024, // 50MB in bytes
  },
}; 