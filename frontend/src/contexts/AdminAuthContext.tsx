import React, { createContext, useContext, useState, useEffect } from 'react';
import { logger, LogCategory } from '../utils/logger';

interface AdminAuthContextType {
  isAdmin: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  checkAdminStatus: () => Promise<boolean>;
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

  const checkAdminStatus = async (): Promise<boolean> => {
    try {
      // TODO: Implement actual API call to check admin status
      const token = localStorage.getItem('adminToken');
      if (!token) {
        setIsAdmin(false);
        setIsAuthenticated(false);
        return false;
      }

      // Mock API call
      const response = await fetch('/api/admin/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setIsAdmin(true);
        setIsAuthenticated(true);
        logger.info(LogCategory.AUTH, 'Admin status verified', null, 'AdminAuth');
        return true;
      } else {
        setIsAdmin(false);
        setIsAuthenticated(false);
        logger.warn(LogCategory.AUTH, 'Admin status check failed', null, 'AdminAuth');
        return false;
      }
    } catch (error) {
      logger.error(LogCategory.ERROR, 'Failed to check admin status', error, 'AdminAuth');
      return false;
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      // TODO: Implement actual API call
      // For development, use hardcoded credentials
      if (username === 'admin' && password === 'admin') {
        const mockToken = 'mock-admin-token';
        localStorage.setItem('adminToken', mockToken);
        setIsAdmin(true);
        setIsAuthenticated(true);
        logger.info(LogCategory.AUTH, 'Admin login successful', null, 'AdminAuth');
        return true;
      }

      logger.warn(LogCategory.AUTH, 'Admin login failed: Invalid credentials', null, 'AdminAuth');
      return false;
    } catch (error) {
      logger.error(LogCategory.ERROR, 'Admin login failed', error, 'AdminAuth');
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('adminToken');
    setIsAdmin(false);
    setIsAuthenticated(false);
    logger.info(LogCategory.AUTH, 'Admin logged out', null, 'AdminAuth');
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
      }}
    >
      {children}
    </AdminAuthContext.Provider>
  );
};
