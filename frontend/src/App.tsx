import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import theme from './theme';
import Dashboard from './components/Dashboard';
import GenerationPage from './components/GenerationPage';
import AdminPanel from './components/AdminPanel';
import AdminLogin from './components/AdminLogin';
import UserPreferences from './components/UserPreferences';
import { AdminAuthProvider } from './contexts/AdminAuthContext';
import { logger, LogCategory } from './utils/logger';
import ProtectedAdminRoute from './components/ProtectedAdminRoute';
import './styles/global.css';

function App() {
  logger.debug(LogCategory.SYSTEM, 'App component rendering', null, 'App');

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider
        maxSnack={3}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        dense
        preventDuplicate
      >
        <AdminAuthProvider>
          <Router>
            <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/generator" element={<GenerationPage />} />
                <Route path="/preferences" element={<UserPreferences />} />
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
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
