import React, { useState, useEffect, useRef, useCallback } from 'react';
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
  CircularProgress,
  Alert,
  LinearProgress,
  Chip,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  BugReport as BugIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Security as SecurityIcon,
  Memory as MemoryIcon,
  NetworkCheck as NetworkIcon,
  Apps as AppsIcon,
  Settings as SettingsIcon,
  Token as TokenIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { logger, LogCategory } from '../utils/logger';
import { SelectChangeEvent } from '@mui/material';
import { useDebugPanel } from '../hooks/useDebugPanel';
import { fetchSystemStats, fetchAgentStatus, SystemStats, AgentStatuses, ModelSettings, TokenUsage, fetchModelSettings, updateModelSettings, fetchTokenUsage, resetTokenUsage, deleteModelSettings, createModelSettings } from '../services/system';

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

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

interface DebugSettings {
  showDebugPanel: boolean;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
  autoScroll: boolean;
}

const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [systemStats, setSystemStats] = useState<SystemStats>({
    cpu_usage: 0,
    memory_usage: {
      total: 0,
      used: 0,
      free: 0,
      percent: 0
    },
    disk_usage: {
      total: 0,
      used: 0,
      free: 0,
      percent: 0
    },
    network_stats: {
      bytes_sent: 0,
      bytes_recv: 0,
      packets_sent: 0,
      packets_recv: 0
    },
    process_count: 0,
    token_usage: 0,
    estimated_cost: 0
  });
  const [agentStatus, setAgentStatus] = useState<AgentStatuses>({});
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [isLoadingAgents, setIsLoadingAgents] = useState(false);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [isLoadingTokens, setIsLoadingTokens] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isVisible, toggle, show, hide } = useDebugPanel();
  const [settings, setSettings] = useState<DebugSettings>({
    showDebugPanel: isVisible,
    logLevel: 'info',
    autoScroll: true,
  });
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [modelSettings, setModelSettings] = useState<Record<string, ModelSettings>>({});
  const [tokenUsage, setTokenUsage] = useState<TokenUsage>({
    total_tokens: 0,
    prompt_tokens: 0,
    completion_tokens: 0,
    estimated_cost: 0,
    last_reset: new Date().toISOString(),
  });
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [isModelDialogOpen, setIsModelDialogOpen] = useState(false);
  const [modelForm, setModelForm] = useState<ModelSettings>({
    model_name: '',
    api_key: '',
    max_tokens: 2000,
    temperature: 0.7,
    is_active: true,
    cost_per_token: 0.0,
  });
  const [panelVisible, setPanelVisible] = useState(true);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  const predefinedModels = [
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    { value: 'ollama', label: 'Ollama' }
  ];

  const fetchData = useCallback(async () => {
    if (!panelVisible) return;

    try {
      setIsLoadingStats(true);
      setIsLoadingAgents(true);
      setIsLoadingModels(true);
      setIsLoadingTokens(true);
      setError(null);

      const [stats, agents, models, usage] = await Promise.all([
        fetchSystemStats(),
        fetchAgentStatus(),
        fetchModelSettings(),
        fetchTokenUsage()
      ]);

      setSystemStats(stats);
      setAgentStatus(agents);
      setModelSettings(models);
      setTokenUsage(usage);
      setLastRefresh(new Date());
      logger.debug(LogCategory.PERFORMANCE, 'System data updated', stats, 'AdminPanel');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch system data';
      setError(errorMessage);
      logger.error(LogCategory.ERROR, errorMessage, error, 'AdminPanel');
    } finally {
      setIsLoadingStats(false);
      setIsLoadingAgents(false);
      setIsLoadingModels(false);
      setIsLoadingTokens(false);
    }
  }, [panelVisible]);

  // Set up visibility observer
  useEffect(() => {
    if (panelRef.current) {
      observerRef.current = new IntersectionObserver(
        ([entry]) => {
          setPanelVisible(entry.isIntersecting);
        },
        { threshold: 0.1 }
      );
      observerRef.current.observe(panelRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  // Fetch data periodically only when visible
  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (panelVisible) {
      fetchData();
      intervalId = setInterval(fetchData, 30000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [panelVisible, fetchData]);

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

  const handleModelDialogOpen = (modelName?: string) => {
    if (modelName) {
      setSelectedModel(modelName);
      setModelForm(modelSettings[modelName]);
    } else {
      setSelectedModel(null);
      setModelForm({
        model_name: '',
        api_key: '',
        max_tokens: 2000,
        temperature: 0.7,
        is_active: true,
        cost_per_token: 0.0,
      });
    }
    setIsModelDialogOpen(true);
  };

  const handleModelDialogClose = () => {
    setIsModelDialogOpen(false);
    setSelectedModel(null);
  };

  const handleModelFormChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = event.target;
    setModelForm((prev: ModelSettings) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleModelSave = async () => {
    try {
      if (selectedModel) {
        // Update existing model
        await updateModelSettings(selectedModel, modelForm);
      } else {
        // Create new model
        await createModelSettings(modelForm);
      }

      const updatedSettings = await fetchModelSettings();
      setModelSettings(updatedSettings);
      handleModelDialogClose();
      logger.info(LogCategory.UI, `Model ${selectedModel ? 'updated' : 'created'} successfully`, modelForm, 'AdminPanel');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save model settings';
      setError(errorMessage);
      logger.error(LogCategory.ERROR, errorMessage, error, 'AdminPanel');
    }
  };

  const handleResetTokenUsage = async () => {
    try {
      await resetTokenUsage();
      const usage = await fetchTokenUsage();
      setTokenUsage(usage);
      logger.info(LogCategory.UI, 'Token usage reset', null, 'AdminPanel');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to reset token usage';
      setError(errorMessage);
      logger.error(LogCategory.ERROR, errorMessage, error, 'AdminPanel');
    }
  };

  const handleModelDelete = async (modelName: string) => {
    try {
      await deleteModelSettings(modelName);
      const updatedSettings = await fetchModelSettings();
      setModelSettings(updatedSettings);
      logger.info(LogCategory.UI, `Model ${modelName} deleted successfully`, null, 'AdminPanel');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete model';
      setError(errorMessage);
      logger.error(LogCategory.ERROR, errorMessage, error, 'AdminPanel');
    }
  };

  const formatBytes = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let value = bytes;
    let unitIndex = 0;
    while (value >= 1024 && unitIndex < units.length - 1) {
      value /= 1024;
      unitIndex++;
    }
    return `${value.toFixed(2)} ${units[unitIndex]}`;
  };

  const formatTimeAgo = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return `${seconds}s ago`;
  };

  if (isLoadingStats || isLoadingAgents || isLoadingModels || isLoadingTokens) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <AdminPanelContainer ref={panelRef}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Admin Dashboard
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Refresh Stats">
            <IconButton onClick={fetchData}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tab icon={<SpeedIcon />} label="Overview" />
        <Tab icon={<AppsIcon />} label="Models" />
        <Tab icon={<BugIcon />} label="Debugging" />
      </Tabs>

      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  CPU Usage
                </Typography>
                {isLoadingStats ? (
                  <CircularProgress size={24} />
                ) : (
                  <Typography variant="h4">
                    {systemStats.cpu_usage.toFixed(1)}%
                  </Typography>
                )}
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Memory Usage
                </Typography>
                {isLoadingStats ? (
                  <CircularProgress size={24} />
                ) : (
                  <Typography variant="h4">
                    {systemStats.memory_usage.percent.toFixed(1)}%
                  </Typography>
                )}
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Disk Usage
                </Typography>
                {isLoadingStats ? (
                  <CircularProgress size={24} />
                ) : (
                  <Typography variant="h4">
                    {systemStats.disk_usage.percent.toFixed(1)}%
                  </Typography>
                )}
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Network Sent
                </Typography>
                {isLoadingStats ? (
                  <CircularProgress size={24} />
                ) : (
                  <Typography variant="h4">
                    {formatBytes(systemStats.network_stats.bytes_sent)}
                  </Typography>
                )}
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Network Received
                </Typography>
                {isLoadingStats ? (
                  <CircularProgress size={24} />
                ) : (
                  <Typography variant="h4">
                    {formatBytes(systemStats.network_stats.bytes_recv)}
                  </Typography>
                )}
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Active Processes
                </Typography>
                {isLoadingStats ? (
                  <CircularProgress size={24} />
                ) : (
                  <Typography variant="h4">
                    {systemStats.process_count}
                  </Typography>
                )}
              </CardContent>
            </StatCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TokenIcon sx={{ mr: 1 }} />
                  <Typography variant="subtitle2">Token Usage</Typography>
                </Box>
                {isLoadingTokens ? (
                  <CircularProgress size={24} />
                ) : (
                  <Typography variant="h4">
                    {systemStats.token_usage.toLocaleString()}
                  </Typography>
                )}
                <Typography variant="body2" color="text.secondary">
                  Estimated Cost: ${systemStats.estimated_cost.toFixed(2)}
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleResetTokenUsage}
                  sx={{ mt: 1 }}
                >
                  Reset Usage
                </Button>
              </CardContent>
            </StatCard>
          </Grid>
        </Grid>

        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Agent Status
          </Typography>
          {isLoadingAgents ? (
            <Grid item xs={12}>
              <CircularProgress />
            </Grid>
          ) : (
            <Grid container spacing={2}>
              {Object.entries(agentStatus).map(([name, status]) => (
                <Grid item xs={12} sm={6} md={4} key={name}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        {name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Typography>
                      <Typography color={status.status === 'active' ? 'success.main' : 'error.main'}>
                        {status.status}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Last Active: {formatTimeAgo(status.last_active)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">AI Model Settings</Typography>
          <Button
            variant="contained"
            startIcon={<SettingsIcon />}
            onClick={() => handleModelDialogOpen()}
          >
            Add Model
          </Button>
        </Box>

        <Grid container spacing={3}>
          {isLoadingModels ? (
            <Grid item xs={12}>
              <CircularProgress />
            </Grid>
          ) : (
            Object.entries(modelSettings).map(([name, settings]) => (
              <Grid item xs={12} md={6} key={name}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6">{name}</Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip
                          label={settings.is_active ? 'Active' : 'Inactive'}
                          color={settings.is_active ? 'success' : 'default'}
                          size="small"
                        />
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleModelDelete(name)}
                          title="Delete Model"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Max Tokens: {settings.max_tokens}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Temperature: {settings.temperature}
                    </Typography>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleModelDialogOpen(name)}
                      sx={{ mt: 2 }}
                    >
                      Edit Settings
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
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

      <Dialog open={isModelDialogOpen} onClose={handleModelDialogClose}>
        <DialogTitle>
          {selectedModel ? 'Edit Model Settings' : 'Add New Model'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Model Name</InputLabel>
              <Select
                value={modelForm.model_name}
                label="Model Name"
                onChange={(e) => setModelForm(prev => ({ ...prev, model_name: e.target.value }))}
                disabled={!!selectedModel}
              >
                {predefinedModels.map((model) => (
                  <MenuItem key={model.value} value={model.value}>
                    {model.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="API Key"
              name="api_key"
              value={modelForm.api_key}
              onChange={handleModelFormChange}
              type="password"
              fullWidth
            />
            <TextField
              label="Max Tokens"
              name="max_tokens"
              value={modelForm.max_tokens}
              onChange={handleModelFormChange}
              type="number"
              fullWidth
            />
            <TextField
              label="Temperature"
              name="temperature"
              value={modelForm.temperature}
              onChange={handleModelFormChange}
              type="number"
              inputProps={{ step: 0.1, min: 0, max: 1 }}
              fullWidth
            />
            <TextField
              label="Cost per 1K Tokens (USD)"
              name="cost_per_token"
              value={modelForm.cost_per_token}
              onChange={handleModelFormChange}
              type="number"
              inputProps={{ step: 0.0001, min: 0 }}
              fullWidth
              helperText="Enter the cost per 1,000 tokens in USD"
            />
            <FormControlLabel
              control={
                <Switch
                  name="is_active"
                  checked={modelForm.is_active}
                  onChange={handleModelFormChange}
                />
              }
              label="Active"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleModelDialogClose}>Cancel</Button>
          <Button onClick={handleModelSave} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </AdminPanelContainer>
  );
};

export default AdminPanel;
