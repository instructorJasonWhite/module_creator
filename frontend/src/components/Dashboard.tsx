import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
  Button,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Description as DocumentIcon,
  School as ModuleIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface ProcessStatus {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'error';
  progress: number;
  timestamp: string;
}

interface RecentModule {
  id: string;
  title: string;
  status: 'draft' | 'published' | 'archived';
  lastModified: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // Mock data - replace with actual API calls
  const activeProcesses: ProcessStatus[] = [
    {
      id: '1',
      name: 'Document Analysis',
      status: 'running',
      progress: 45,
      timestamp: '2024-03-29T10:30:00',
    },
    {
      id: '2',
      name: 'Content Generation',
      status: 'completed',
      progress: 100,
      timestamp: '2024-03-29T10:25:00',
    },
  ];

  const recentModules: RecentModule[] = [
    {
      id: '1',
      title: 'Introduction to Python',
      status: 'published',
      lastModified: '2024-03-29T10:00:00',
    },
    {
      id: '2',
      title: 'Web Development Basics',
      status: 'draft',
      lastModified: '2024-03-29T09:30:00',
    },
  ];

  const handleStartGeneration = () => {
    navigate('/generation');
  };

  const handleProcessAction = (processId: string, action: 'start' | 'stop' | 'delete') => {
    // TODO: Implement process actions
    console.log(`Action ${action} on process ${processId}`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'primary';
      case 'completed':
        return 'success';
      case 'error':
        return 'error';
      case 'published':
        return 'success';
      case 'draft':
        return 'warning';
      case 'archived':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">Quick Actions</Typography>
              <Button
                variant="contained"
                startIcon={<DocumentIcon />}
                onClick={handleStartGeneration}
              >
                Start New Generation
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Active Processes */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Active Processes</Typography>
              <IconButton>
                <RefreshIcon />
              </IconButton>
            </Box>
            <List>
              {activeProcesses.map((process) => (
                <ListItem
                  key={process.id}
                  secondaryAction={
                    <Box>
                      {process.status === 'running' && (
                        <IconButton
                          edge="end"
                          onClick={() => handleProcessAction(process.id, 'stop')}
                        >
                          <StopIcon />
                        </IconButton>
                      )}
                      <IconButton
                        edge="end"
                        onClick={() => handleProcessAction(process.id, 'delete')}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  }
                >
                  <ListItemIcon>
                    <PlayIcon color={process.status === 'running' ? 'primary' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText
                    primary={process.name}
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          label={process.status}
                          color={getStatusColor(process.status)}
                          size="small"
                        />
                        <Typography variant="caption" color="text.secondary">
                          {new Date(process.timestamp).toLocaleTimeString()}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Recent Modules */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Recent Modules</Typography>
            <List>
              {recentModules.map((module) => (
                <ListItem
                  key={module.id}
                  button
                  onClick={() => navigate(`/modules/${module.id}`)}
                >
                  <ListItemIcon>
                    <ModuleIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={module.title}
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          label={module.status}
                          color={getStatusColor(module.status)}
                          size="small"
                        />
                        <Typography variant="caption" color="text.secondary">
                          Last modified: {new Date(module.lastModified).toLocaleString()}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 