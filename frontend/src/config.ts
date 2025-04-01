import { logger, LogCategory } from './utils/logger';
import api from './utils/axios';

const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
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
      preferences: {
        me: '/api/v1/preferences/me',
      },
    },
  },
  upload: {
    maxFileSize: 50 * 1024 * 1024, // 50MB in bytes
  },
};

export { api };
