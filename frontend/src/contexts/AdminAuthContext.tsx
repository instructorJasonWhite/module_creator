import React, { createContext, useContext, useState, useEffect } from 'react';
import { logger, LogCategory } from '../utils/logger';

interface AdminAuthContextType {
  isAdmin: boolean;
  isAuthenticated: boolean;
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
  const [error, setError] = useState<string | null>(null);

  const checkAdminStatus = async (): Promise<boolean> => {
    try {
      setError(null);
      const token = localStorage.getItem('adminToken');
      if (!token) {
        setIsAdmin(false);
        setIsAuthenticated(false);
        logger.debug(LogCategory.AUTH, 'No token found in localStorage', null, 'AdminAuth');
        return false;
      }

      logger.debug(LogCategory.AUTH, 'Checking admin status with token', null, 'AdminAuth');
      const response = await fetch('http://localhost:8000/api/v1/auth/verify', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setIsAdmin(true);
        setIsAuthenticated(true);
        logger.info(LogCategory.AUTH, `Admin status verified for user: ${data.username}`, null, 'AdminAuth');
        return true;
      } else {
        const errorData = await response.json();
        setIsAdmin(false);
        setIsAuthenticated(false);
        setError(errorData.detail || 'Failed to verify admin status');
        logger.warn(LogCategory.AUTH, `Admin status check failed: ${errorData.detail}`, null, 'AdminAuth');
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(errorMessage);
      logger.error(LogCategory.ERROR, `Failed to check admin status: ${errorMessage}`, error, 'AdminAuth');
      return false;
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setError(null);
      logger.debug(LogCategory.AUTH, `Attempting login for user: ${username}`, null, 'AdminAuth');

      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('adminToken', data.access_token);
        setIsAdmin(true);
        setIsAuthenticated(true);
        logger.info(LogCategory.AUTH, `Login successful for user: ${username}`, null, 'AdminAuth');
        return true;
      } else {
        setError(data.detail || 'Login failed');
        logger.warn(LogCategory.AUTH, `Login failed: ${data.detail}`, null, 'AdminAuth');
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(errorMessage);
      logger.error(LogCategory.ERROR, `Login failed: ${errorMessage}`, error, 'AdminAuth');
      return false;
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

  useEffect(() => {
    checkAdminStatus();
  }, []);

  return (
    <AdminAuthContext.Provider
      value={{
        isAdmin,
        isAuthenticated,
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
