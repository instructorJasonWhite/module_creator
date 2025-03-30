import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Collapse,
  IconButton,
  Divider,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { logger, LogCategory } from '../utils/logger';
import { useNavigate } from 'react-router-dom';
import { config } from '../config';
import CloseIcon from '@mui/icons-material/Close';

const LoginContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  maxWidth: 400,
  margin: 'auto',
  background: theme.palette.background.paper,
  boxShadow: theme.shadows[3],
  position: 'relative',
  zIndex: 1,
}));

const DebugBox = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(2),
  padding: theme.spacing(2),
  backgroundColor: theme.palette.grey[100],
  borderRadius: theme.shape.borderRadius,
  width: '100%',
  fontFamily: 'monospace',
  fontSize: '0.875rem',
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-all',
}));

const AdminLogin: React.FC = () => {
  const { login, error } = useAdminAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState<string[]>([]);
  const [showDebug, setShowDebug] = useState(true);

  const addDebugInfo = (message: string) => {
    console.log(message);
    setDebugInfo(prev => [...prev, `${new Date().toISOString()} - ${message}`]);
    logger.debug(LogCategory.AUTH, message, null, 'AdminLogin');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted');
    setIsLoading(true);
    setDebugInfo([]);
    addDebugInfo('Login attempt started');
    addDebugInfo(`Username: ${username}`);
    addDebugInfo(`API URL: ${config.api.baseUrl}${config.api.endpoints.auth.login}`);

    try {
      addDebugInfo('Calling login function...');
      console.log('About to call login function');
      const success = await login(username, password);
      console.log('Login function returned:', success);
      addDebugInfo(`Login result: ${success}`);
      
      if (success) {
        addDebugInfo('Login successful, navigating to /admin');
        navigate('/admin');
      } else {
        addDebugInfo(`Login failed: ${error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Login error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      addDebugInfo(`Login error: ${errorMessage}`);
      logger.error(LogCategory.ERROR, `Admin login error: ${errorMessage}`, err, 'AdminLogin');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 0,
      }}
    >
      <LoginContainer elevation={3}>
        <Typography variant="h5" component="h1" gutterBottom>
          Admin Login
        </Typography>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Access the admin dashboard
        </Typography>

        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username"
            name="username"
            autoComplete="username"
            autoFocus
            value={username}
            onChange={(e) => {
              console.log('Username changed:', e.target.value);
              setUsername(e.target.value);
            }}
            disabled={isLoading}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => {
              console.log('Password changed');
              setPassword(e.target.value);
            }}
            disabled={isLoading}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
            onClick={() => console.log('Submit button clicked')}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Login'}
          </Button>
        </Box>

        <Divider sx={{ width: '100%', my: 2 }} />
        
        <Box sx={{ width: '100%' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle2" color="textSecondary">
              Debug Information
            </Typography>
            <IconButton size="small" onClick={() => setShowDebug(!showDebug)}>
              <CloseIcon sx={{ transform: showDebug ? 'rotate(180deg)' : 'none' }} />
            </IconButton>
          </Box>
          <Collapse in={showDebug}>
            <DebugBox>
              {debugInfo.map((info, index) => (
                <div key={index}>{info}</div>
              ))}
            </DebugBox>
          </Collapse>
        </Box>
      </LoginContainer>
    </Box>
  );
};

export default AdminLogin;
