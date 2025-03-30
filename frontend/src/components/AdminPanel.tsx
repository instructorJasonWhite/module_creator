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
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
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
  Add as AddIcon,
  Edit as EditIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { logger, LogCategory } from '../utils/logger';
import { SelectChangeEvent } from '@mui/material';
import { useDebugPanel } from '../hooks/useDebugPanel';
import {
  Agent,
  AgentContext,
  AgentStatuses,
  ModelSettings,
  SystemStats,
  TokenUsage,
  createModelSettings,
  deleteAgentContext,
  deleteModelSettings,
  fetchAgents,
  fetchModelSettings,
  fetchSystemStats,
  fetchTokenUsage,
  resetTokenUsage,
  updateModelSettings,
  updateAgentContext,
  createAgentContext,
} from '../services/system';
import { useNavigate } from 'react-router-dom';

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
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface DebugSettings {
  showDebugPanel: boolean;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
  autoScroll: boolean;
}

const AdminPanel: React.FC = () => {
  const [tab, setTab] = useState(0);
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
    provider: 'openai',
    base_url: 'http://localhost:11434'
  });
  const [panelVisible, setPanelVisible] = useState(true);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [contextDialogOpen, setContextDialogOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [newContext, setNewContext] = useState<AgentContext>({
    context_id: crypto.randomUUID(),
    context: '',
    priority: 0,
    is_active: true,
  });
  const navigate = useNavigate();

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
        fetchAgents(),
        fetchModelSettings(),
        fetchTokenUsage()
      ]);

      setSystemStats(stats);
      setAgents(agents);
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
    setTab(newValue);
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
        provider: 'openai',
        base_url: 'http://localhost:11434'
      });
    }
    setIsModelDialogOpen(true);
  };

  const handleModelDialogClose = () => {
    setIsModelDialogOpen(false);
    setSelectedModel(null);
  };

  const handleModelFormChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent<string>
  ) => {
    const { name, value } = event.target;
    setModelForm(prev => ({
      ...prev,
      [name]: value
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

  const handleContextDialogOpen = (agent: Agent) => {
    setSelectedAgent(agent);
    setContextDialogOpen(true);
  };

  const handleContextDialogClose = () => {
    setContextDialogOpen(false);
    setSelectedAgent(null);
    setNewContext({
      context_id: crypto.randomUUID(),
      context: '',
      priority: 0,
      is_active: true,
    });
  };

  const handleContextSave = async () => {
    if (!selectedAgent) return;

    try {
      await createAgentContext(newContext);
      const updatedAgents = await fetchAgents();
      setAgents(updatedAgents);
      handleContextDialogClose();
    } catch (error) {
      console.error('Error saving context:', error);
    }
  };

  const handleContextDelete = async (contextId: string) => {
    try {
      await deleteAgentContext(contextId);
      const updatedAgents = await fetchAgents();
      setAgents(updatedAgents);
    } catch (error) {
      console.error('Error deleting context:', error);
    }
  };

  const handleMoveToGeneration = () => {
    logger.info(LogCategory.UI, 'Navigating to generation page', null, 'AdminPanel');
    navigate('/generation');
  };

  const handleAgentContextChange = (agent: Agent, newContext: string) => {
    const updatedAgents = agents.map((a) => {
      if (a.name === agent.name) {
        return {
          ...a,
          contexts: [
            {
              context_id: crypto.randomUUID(),
              context: newContext,
              priority: 0,
              is_active: true,
            },
          ],
        };
      }
      return a;
    });
    setAgents(updatedAgents);
  };

  if (isLoadingStats || isLoadingAgents || isLoadingModels || isLoadingTokens) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const renderModelDialog = () => (
    <Dialog open={isModelDialogOpen} onClose={handleModelDialogClose} maxWidth="sm" fullWidth>
      <DialogTitle>{selectedModel ? 'Edit Model' : 'Add New Model'}</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Model Name"
            name="model_name"
            value={modelForm.model_name}
            onChange={handleModelFormChange}
            fullWidth
            required
          />
          
          <FormControl fullWidth>
            <InputLabel>Provider</InputLabel>
            <Select
              name="provider"
              value={modelForm.provider}
              onChange={handleModelFormChange}
              label="Provider"
            >
              <MenuItem value="openai">OpenAI</MenuItem>
              <MenuItem value="ollama">Ollama</MenuItem>
            </Select>
          </FormControl>

          {modelForm.provider === 'openai' && (
            <TextField
              label="API Key"
              name="api_key"
              value={modelForm.api_key}
              onChange={handleModelFormChange}
              type="password"
              fullWidth
            />
          )}

          {modelForm.provider === 'ollama' && (
            <TextField
              label="Base URL"
              name="base_url"
              value={modelForm.base_url}
              onChange={handleModelFormChange}
              fullWidth
              placeholder="http://localhost:11434"
            />
          )}

          <TextField
            label="Max Tokens"
            name="max_tokens"
            type="number"
            value={modelForm.max_tokens}
            onChange={handleModelFormChange}
            fullWidth
            required
          />

          <TextField
            label="Temperature"
            name="temperature"
            type="number"
            value={modelForm.temperature}
            onChange={handleModelFormChange}
            fullWidth
            required
            inputProps={{ min: 0, max: 2, step: 0.1 }}
          />

          <TextField
            label="Cost per Token (USD/1K)"
            name="cost_per_token"
            type="number"
            value={modelForm.cost_per_token}
            onChange={handleModelFormChange}
            fullWidth
            required
            inputProps={{ min: 0, step: 0.0001 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={modelForm.is_active}
                onChange={(e) => setModelForm(prev => ({ ...prev, is_active: e.target.checked }))}
              />
            }
            label="Active"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleModelDialogClose}>Cancel</Button>
        <Button onClick={handleModelSave} variant="contained" color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <AdminPanelContainer ref={panelRef}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Admin Dashboard
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Button
            variant="contained"
            color="error"
            size="large"
            onClick={handleMoveToGeneration}
            sx={{ mr: 2 }}
          >
            Move to Generation
          </Button>
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

      <Tabs value={tab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tab icon={<SpeedIcon />} label="Overview" />
        <Tab icon={<AppsIcon />} label="Models" />
        <Tab icon={<BugIcon />} label="Debugging" />
        <Tab icon={<AddIcon />} label="Agents" />
      </Tabs>

      <TabPanel value={tab} index={0}>
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
              {agents.map((agent) => (
                <Grid item xs={12} sm={6} md={4} key={agent.name}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        {agent.name.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      </Typography>
                      <Typography color={agent.is_active ? 'success.main' : 'error.main'}>
                        {agent.status}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Last Active: {formatTimeAgo(agent.last_active)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </TabPanel>

      <TabPanel value={tab} index={1}>
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

      <TabPanel value={tab} index={2}>
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

      <TabPanel value={tab} index={3}>
        {isLoadingAgents ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        ) : agents.length === 0 ? (
          <Alert severity="info" sx={{ mb: 2 }}>
            No agents available. Please check if the backend server is running.
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {agents.map((agent) => (
              <Grid item xs={12} md={6} key={agent.name}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6">{agent.name}</Typography>
                      <Chip
                        label={agent.status}
                        color={agent.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {agent.description}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Role: {agent.role}
                    </Typography>
                    <Divider sx={{ my: 2 }} />
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Additional Context
                      </Typography>
                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        placeholder="Enter any additional context to be appended to this agent's prompt..."
                        value={agent.contexts[0]?.context || ''}
                        onChange={(e) => {
                          handleAgentContextChange(agent, e.target.value);
                        }}
                      />
                      <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-end' }}>
                        <Button
                          variant="contained"
                          color="primary"
                          size="small"
                          onClick={async () => {
                            try {
                              const context = agent.contexts[0] || {
                                context_id: crypto.randomUUID(),
                                context: '',
                                priority: 0,
                                is_active: true,
                              };
                              await updateAgentContext(agent.name, context);
                              const updatedAgents = await fetchAgents();
                              setAgents(updatedAgents);
                              logger.info(LogCategory.API, `Context updated for agent ${agent.name}`, null, 'AdminPanel');
                            } catch (error) {
                              logger.error(LogCategory.ERROR, `Failed to update context for agent ${agent.name}`, error, 'AdminPanel');
                              setError('Failed to save context changes');
                            }
                          }}
                        >
                          Save Context
                        </Button>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      {renderModelDialog()}

      <Dialog open={contextDialogOpen} onClose={handleContextDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>Add Context</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Context"
            fullWidth
            multiline
            rows={4}
            value={newContext.context}
            onChange={(e) =>
              setNewContext((prev: AgentContext) => ({ ...prev, context: e.target.value }))
            }
          />
          <TextField
            margin="dense"
            label="Priority"
            type="number"
            fullWidth
            value={newContext.priority}
            onChange={(e) =>
              setNewContext((prev: AgentContext) => ({ ...prev, priority: parseInt(e.target.value) || 0 }))
            }
          />
          <FormControlLabel
            control={
              <Switch
                checked={newContext.is_active}
                onChange={(e) =>
                  setNewContext((prev: AgentContext) => ({ ...prev, is_active: e.target.checked }))
                }
              />
            }
            label="Active"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleContextDialogClose}>Cancel</Button>
          <Button onClick={handleContextSave} startIcon={<SaveIcon />}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </AdminPanelContainer>
  );
};

export default AdminPanel;
