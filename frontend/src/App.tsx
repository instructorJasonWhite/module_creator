import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import theme from './theme';
import Dashboard from './components/Dashboard';
import GenerationPage from './components/GenerationPage';
import AdminPanel from './components/AdminPanel';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/generation" element={<GenerationPage />} />
            <Route path="/admin" element={<AdminPanel />} />
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
