import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { logger, LogCategory } from '../utils/logger';

interface ProtectedAdminRouteProps {
  children: React.ReactNode;
}

const ProtectedAdminRoute: React.FC<ProtectedAdminRouteProps> = ({ children }) => {
  const { isAdmin, isAuthenticated } = useAdminAuth();
  const location = useLocation();

  if (!isAuthenticated || !isAdmin) {
    logger.warn(
      LogCategory.AUTH,
      'Unauthorized admin access attempt',
      { path: location.pathname },
      'ProtectedAdminRoute'
    );
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  logger.info(
    LogCategory.AUTH,
    'Admin access granted',
    { path: location.pathname },
    'ProtectedAdminRoute'
  );

  return <>{children}</>;
};

export default ProtectedAdminRoute;
