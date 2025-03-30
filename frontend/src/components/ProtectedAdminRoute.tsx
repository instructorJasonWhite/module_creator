import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { logger, LogCategory } from '../utils/logger';
import { CircularProgress, Box } from '@mui/material';

interface ProtectedAdminRouteProps {
  children: React.ReactNode;
}

const ProtectedAdminRoute: React.FC<ProtectedAdminRouteProps> = ({ children }) => {
  const { isAdmin, isAuthenticated, isLoading } = useAdminAuth();
  const location = useLocation();

  logger.debug(
    LogCategory.AUTH,
    `ProtectedAdminRoute render: isLoading=${isLoading}, isAuthenticated=${isAuthenticated}, isAdmin=${isAdmin}`,
    { path: location.pathname },
    'ProtectedAdminRoute'
  );

  if (isLoading) {
    logger.debug(LogCategory.AUTH, 'Showing loading spinner', null, 'ProtectedAdminRoute');
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated || !isAdmin) {
    logger.warn(
      LogCategory.AUTH,
      'Unauthorized admin access attempt, redirecting to login',
      { path: location.pathname, isAuthenticated, isAdmin },
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
