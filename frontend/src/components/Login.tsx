import React, { useState } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { TextField, Button, Box, Typography, Alert } from '@mui/material';
import { logger, LogCategory } from '../utils/logger';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, error } = useAdminAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      logger.debug(LogCategory.AUTH, 'Attempting login', { username }, 'Login');
      const success = await login(username, password);

      if (success) {
        logger.info(LogCategory.AUTH, 'Login successful', { username }, 'Login');
      } else {
        logger.warn(LogCategory.AUTH, 'Login failed', { username }, 'Login');
      }
    } catch (err) {
      logger.error(LogCategory.ERROR, 'Login error', err, 'Login');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 2,
        maxWidth: 400,
        mx: 'auto',
        mt: 4,
        p: 3,
      }}
    >
      <Typography variant="h4" component="h1" gutterBottom>
        Admin Login
      </Typography>

      {error && (
        <Alert severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      )}

      <TextField
        label="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        fullWidth
        required
        disabled={isLoading}
      />

      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        fullWidth
        required
        disabled={isLoading}
      />

      <Button
        type="submit"
        variant="contained"
        color="primary"
        fullWidth
        disabled={isLoading}
      >
        {isLoading ? 'Logging in...' : 'Login'}
      </Button>
    </Box>
  );
};
