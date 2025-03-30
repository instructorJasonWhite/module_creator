import React, { createContext, useContext, useState, useEffect } from 'react';
import { logger, LogCategory } from '../utils/logger';
import { config } from '../config';

interface AdminAuthContextType {
  isAdmin: boolean;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  checkAdminStatus: () => Promise<boolean>;
  error: string | null;
}

const AdminAuthContext = createContext<AdminAuthContextType | undefined>(undefined);

export const useAdminAuth = () => {
  const context = useContext(AdminAuthContext);
  if (!context) {
    throw new Error('useAdminAuth must be used within an AdminAuthProvider');
  }
  return context;
};

export const AdminAuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkAdminStatus = async (): Promise<boolean> => {
    try {
      logger.debug(LogCategory.AUTH, 'Starting admin status check', null, 'AdminAuth');
      setError(null);
      const token = localStorage.getItem('adminToken');
      
      if (!token) {
        logger.debug(LogCategory.AUTH, 'No token found in localStorage', null, 'AdminAuth');
        setIsAdmin(false);
        setIsAuthenticated(false);
        return false;
      }

      logger.debug(LogCategory.AUTH, 'Found token, verifying with backend', null, 'AdminAuth');
      const response = await fetch(`${config.api.baseUrl}${config.api.endpoints.auth.verify}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });

      logger.debug(LogCategory.AUTH, `Backend response status: ${response.status}`, null, 'AdminAuth');

      if (response.ok) {
        const data = await response.json();
        logger.debug(LogCategory.AUTH, `Verification successful: ${JSON.stringify(data)}`, null, 'AdminAuth');
        setIsAdmin(true);
        setIsAuthenticated(true);
        return true;
      } else {
        const errorData = await response.json();
        logger.warn(LogCategory.AUTH, `Verification failed: ${JSON.stringify(errorData)}`, null, 'AdminAuth');
        setIsAdmin(false);
        setIsAuthenticated(false);
        localStorage.removeItem('adminToken');
        setError(errorData.detail || 'Failed to verify admin status');
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      logger.error(LogCategory.ERROR, `Admin status check failed: ${errorMessage}`, error, 'AdminAuth');
      setError(errorMessage);
      return false;
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    console.log('AdminAuthContext: login function called');
    try {
      setIsLoading(true);
      setError(null);
      console.log('AdminAuthContext: Starting login process');
      logger.debug(LogCategory.AUTH, `Attempting login for user: ${username}`, null, 'AdminAuth');

      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const url = `${config.api.baseUrl}${config.api.endpoints.auth.login}`;
      console.log('AdminAuthContext: Login URL:', url);
      console.log('AdminAuthContext: Request body:', formData.toString());
      logger.debug(LogCategory.AUTH, `Login URL: ${url}`, null, 'AdminAuth');
      logger.debug(LogCategory.AUTH, `Request body: ${formData.toString()}`, null, 'AdminAuth');

      // Test the connection first
      try {
        console.log('AdminAuthContext: Testing backend connection...');
        const testResponse = await fetch(config.api.baseUrl);
        console.log('AdminAuthContext: Backend connection test status:', testResponse.status);
        if (!testResponse.ok) {
          console.error('AdminAuthContext: Backend connection test failed:', await testResponse.text());
          throw new Error(`Backend connection test failed with status: ${testResponse.status}`);
        }
      } catch (e) {
        console.error('AdminAuthContext: Backend connection error:', e);
        const errorMessage = e instanceof Error ? e.message : 'Failed to connect to backend';
        throw new Error(`Cannot connect to backend server: ${errorMessage}`);
      }

      let response;
      try {
        console.log('AdminAuthContext: Sending login request...');
        response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
          },
          body: formData.toString(),
        });
        console.log('AdminAuthContext: Login response status:', response.status);
        console.log('AdminAuthContext: Response headers:', Object.fromEntries(response.headers.entries()));
      } catch (e) {
        console.error('AdminAuthContext: Login request failed:', e);
        const errorMessage = e instanceof Error ? e.message : 'Network error';
        throw new Error(`Login request failed: ${errorMessage}`);
      }

      let data;
      try {
        console.log('AdminAuthContext: Reading response body...');
        const responseText = await response.text();
        console.log('AdminAuthContext: Raw response:', responseText);
        if (!responseText) {
          throw new Error('Empty response from server');
        }
        data = JSON.parse(responseText);
        console.log('AdminAuthContext: Parsed response:', data);
      } catch (e) {
        console.error('AdminAuthContext: Failed to parse response:', e);
        throw new Error('Invalid response from server');
      }

      if (response.ok) {
        const newToken = data.access_token;
        localStorage.setItem('adminToken', newToken);
        setIsAdmin(true);
        setIsAuthenticated(true);
        console.log('AdminAuthContext: Login successful');
        return true;
      } else {
        const errorMessage = data.detail || 'Login failed';
        setError(errorMessage);
        console.log('AdminAuthContext: Login failed:', errorMessage);
        return false;
      }
    } catch (error) {
      console.error('AdminAuthContext: Login error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    try {
      localStorage.removeItem('adminToken');
      setIsAdmin(false);
      setIsAuthenticated(false);
      setError(null);
      logger.info(LogCategory.AUTH, 'Admin logged out successfully', null, 'AdminAuth');
    } catch (error) {
      logger.error(LogCategory.ERROR, 'Error during logout', error, 'AdminAuth');
    }
  };

  // Check auth status on mount
  useEffect(() => {
    const initializeAuth = async () => {
      logger.debug(LogCategory.AUTH, 'Initializing auth state', null, 'AdminAuth');
      await checkAdminStatus();
      setIsLoading(false);
      logger.debug(LogCategory.AUTH, `Auth state initialized: isAdmin=${isAdmin}, isAuthenticated=${isAuthenticated}`, null, 'AdminAuth');
    };

    initializeAuth();
  }, []);

  return (
    <AdminAuthContext.Provider
      value={{
        isAdmin,
        isAuthenticated,
        isLoading,
        login,
        logout,
        checkAdminStatus,
        error,
      }}
    >
      {children}
    </AdminAuthContext.Provider>
  );
};
