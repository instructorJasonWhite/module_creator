import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import theme from './theme';
import Dashboard from './components/Dashboard';
import GenerationPage from './components/GenerationPage';
import AdminPanel from './components/AdminPanel';
import AdminLogin from './components/AdminLogin';
import { AdminAuthProvider } from './contexts/AdminAuthContext';
import { logger, LogCategory } from './utils/logger';
import ProtectedAdminRoute from './components/ProtectedAdminRoute';

function App() {
  logger.debug(LogCategory.SYSTEM, 'App component rendering', null, 'App');

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AdminAuthProvider>
        <Router>
          <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/generate" element={<GenerationPage />} />
              <Route path="/login" element={<Navigate to="/admin/login" replace />} />
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route
                path="/admin"
                element={
                  <ProtectedAdminRoute>
                    <AdminPanel />
                  </ProtectedAdminRoute>
                }
              />
            </Routes>
          </Box>
        </Router>
      </AdminAuthProvider>
    </ThemeProvider>
  );
}

export default App;
