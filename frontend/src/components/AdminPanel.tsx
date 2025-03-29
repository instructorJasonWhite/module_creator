import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  BugReport as BugIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { logger, LogCategory } from '../utils/logger';
import { SelectChangeEvent } from '@mui/material';
import { useDebugPanel } from '../hooks/useDebugPanel';

// Styled components
const AdminPanelContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  background: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(10px)',
}));

const StatCard = styled(Card)(({ theme }) => ({
  height: '100%',
  background: 'rgba(255, 255, 255, 0.8)',
  backdropFilter: 'blur(5px)',
  transition: 'transform 0.2s',
  '&:hover': {
    transform: 'translateY(-4px)',
  },
}));

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} style={{ padding: '20px 0' }}>
    {value === index && <Box>{children}</Box>}
  </div>
);

interface DebugSettings {
  showDebugPanel: boolean;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
  autoScroll: boolean;
}

const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [systemStats, setSystemStats] = useState({
    activeAgents: 0,
    totalRequests: 0,
    averageResponseTime: 0,
    errorRate: 0,
    memoryUsage: 0,
    cpuUsage: 0,
  });
  const { isVisible, toggle, show, hide } = useDebugPanel();
  const [settings, setSettings] = useState<DebugSettings>({
    showDebugPanel: isVisible,
    logLevel: 'info',
    autoScroll: true,
  });

  // Fetch system stats periodically
  useEffect(() => {
    const fetchStats = async () => {
      try {
        // TODO: Implement actual API call
        const mockStats = {
          activeAgents: Math.floor(Math.random() * 5),
          totalRequests: Math.floor(Math.random() * 1000),
          averageResponseTime: Math.floor(Math.random() * 500),
          errorRate: Math.random() * 0.1,
          memoryUsage: Math.floor(Math.random() * 80),
          cpuUsage: Math.floor(Math.random() * 60),
        };
        setSystemStats(mockStats);
        logger.debug(LogCategory.PERFORMANCE, 'System stats updated', mockStats, 'AdminPanel');
      } catch (error) {
        logger.error(LogCategory.ERROR, 'Failed to fetch system stats', error, 'AdminPanel');
      }
    };

    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    logger.info(LogCategory.UI, `Admin panel tab changed to ${newValue}`, null, 'AdminPanel');
  };

  const handleDebugSettingChange = (
    event: React.ChangeEvent<HTMLInputElement> | SelectChangeEvent<string>
  ) => {
    const target = event.target as HTMLInputElement | { name: string; value: string };
    const { name, value } = target;

    if ('checked' in target) {
      const checked = target.checked;
      setSettings(prev => ({ ...prev, [name]: checked }));
      if (name === 'showDebugPanel') {
        checked ? show() : hide();
      }
    } else {
      setSettings(prev => ({ ...prev, [name]: value }));
    }

    logger.info(LogCategory.UI, `Debug setting changed: ${name} = ${'checked' in target ? target.checked : value}`, null, 'AdminPanel');
  };

  const handleRefreshStats = () => {
    logger.info(LogCategory.UI, 'Manual stats refresh requested', null, 'AdminPanel');
    // TODO: Implement manual refresh
  };

  return (
    <AdminPanelContainer>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Admin Dashboard
        </Typography>
        <Tooltip title="Refresh Stats">
          <IconButton onClick={handleRefreshStats}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tab icon={<SpeedIcon />} label="Performance" />
        <Tab icon={<BugIcon />} label="Debugging" />
        <Tab icon={<StorageIcon />} label="Storage" />
        <Tab icon={<SecurityIcon />} label="Security" />
      </Tabs>

      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Active Agents
                </Typography>
                <Typography variant="h4">
                  {systemStats.activeAgents}
                </Typography>
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Requests
                </Typography>
                <Typography variant="h4">
                  {systemStats.totalRequests}
                </Typography>
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Avg Response Time
                </Typography>
                <Typography variant="h4">
                  {systemStats.averageResponseTime}ms
                </Typography>
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Error Rate
                </Typography>
                <Typography variant="h4" color="error">
                  {(systemStats.errorRate * 100).toFixed(1)}%
                </Typography>
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Memory Usage
                </Typography>
                <Typography variant="h4">
                  {systemStats.memoryUsage}%
                </Typography>
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  CPU Usage
                </Typography>
                <Typography variant="h4">
                  {systemStats.cpuUsage}%
                </Typography>
              </CardContent>
            </StatCard>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Box sx={{ maxWidth: 600 }}>
          <Typography variant="h6" gutterBottom>
            Debug Settings
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={settings.showDebugPanel}
                onChange={handleDebugSettingChange}
                name="showDebugPanel"
              />
            }
            label="Show Debug Panel"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.autoScroll}
                onChange={handleDebugSettingChange}
                name="autoScroll"
              />
            }
            label="Auto-scroll Logs"
          />
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Log Level</InputLabel>
            <Select
              value={settings.logLevel}
              label="Log Level"
              onChange={handleDebugSettingChange}
              name="logLevel"
            >
              <MenuItem value="debug">Debug</MenuItem>
              <MenuItem value="info">Info</MenuItem>
              <MenuItem value="warn">Warn</MenuItem>
              <MenuItem value="error">Error</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Typography variant="h6" gutterBottom>
          Storage Management
        </Typography>
        {/* TODO: Implement storage management interface */}
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Typography variant="h6" gutterBottom>
          Security Settings
        </Typography>
        {/* TODO: Implement security settings interface */}
      </TabPanel>
    </AdminPanelContainer>
  );
};

export default AdminPanel;
