import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  Close as CloseIcon,
  Clear as ClearIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { logger, LogCategory, LogLevel } from '../utils/logger';

// Styled components
const DebugPanelContainer = styled(Paper)(({ theme }) => ({
  position: 'fixed',
  bottom: 0,
  right: 0,
  width: '100%',
  maxHeight: '50vh',
  display: 'flex',
  flexDirection: 'column',
  zIndex: 9999,
  background: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(10px)',
}));

const LogEntry = styled(Box)<{ level: LogLevel }>(({ theme, level }) => ({
  padding: theme.spacing(1),
  borderLeft: `4px solid ${getLevelColor(level)}`,
  marginBottom: theme.spacing(0.5),
  '&:hover': {
    background: 'rgba(0, 0, 0, 0.04)',
  },
}));

const LogTimestamp = styled(Typography)(({ theme }) => ({
  fontSize: '0.8rem',
  color: theme.palette.text.secondary,
}));

const LogMessage = styled(Typography)(({ theme }) => ({
  fontSize: '0.9rem',
  fontFamily: 'monospace',
}));

const LogDetails = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(0.5),
  padding: theme.spacing(1),
  background: 'rgba(0, 0, 0, 0.02)',
  borderRadius: theme.shape.borderRadius,
  fontSize: '0.8rem',
  fontFamily: 'monospace',
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-word',
}));

const FilterChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
}));

// Helper function to get color for log level
const getLevelColor = (level: LogLevel): string => {
  switch (level) {
    case LogLevel.ERROR:
      return '#FF0000';
    case LogLevel.WARN:
      return '#FFA500';
    case LogLevel.INFO:
      return '#008000';
    case LogLevel.DEBUG:
      return '#0000FF';
    default:
      return '#000000';
  }
};

interface DebugPanelProps {
  onClose: () => void;
}

const DebugPanel: React.FC<DebugPanelProps> = ({ onClose }) => {
  const [logs, setLogs] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLevel, setSelectedLevel] = useState<LogLevel | 'ALL'>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<LogCategory | 'ALL'>('ALL');
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Subscribe to log updates
  useEffect(() => {
    const updateLogs = () => {
      setLogs(logger.getLogs());
    };

    // Update logs every second
    const interval = setInterval(updateLogs, 1000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  // Filter logs based on search term and selected filters
  const filteredLogs = logs.filter(log => {
    const matchesSearch = searchTerm === '' ||
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      JSON.stringify(log.details).toLowerCase().includes(searchTerm.toLowerCase());

    const matchesLevel = selectedLevel === 'ALL' || log.level === selectedLevel;
    const matchesCategory = selectedCategory === 'ALL' || log.category === selectedCategory;

    return matchesSearch && matchesLevel && matchesCategory;
  });

  const handleClearLogs = () => {
    logger.clearLogs();
    setLogs([]);
  };

  const toggleAutoScroll = () => {
    setAutoScroll(!autoScroll);
  };

  return (
    <DebugPanelContainer>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6">Debug Panel</Typography>
        <Box>
          <Tooltip title={autoScroll ? "Disable auto-scroll" : "Enable auto-scroll"}>
            <IconButton onClick={toggleAutoScroll} size="small">
              <FilterIcon color={autoScroll ? "primary" : "inherit"} />
            </IconButton>
          </Tooltip>
          <Tooltip title="Clear logs">
            <IconButton onClick={handleClearLogs} size="small">
              <ClearIcon />
            </IconButton>
          </Tooltip>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </Box>

      <Divider />

      <Box sx={{ p: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField
          size="small"
          placeholder="Search logs..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
          }}
        />

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Level</InputLabel>
          <Select
            value={selectedLevel}
            label="Level"
            onChange={(e) => setSelectedLevel(e.target.value as LogLevel | 'ALL')}
          >
            <MenuItem value="ALL">All Levels</MenuItem>
            {Object.values(LogLevel).map((level) => (
              <MenuItem key={level} value={level}>
                {level}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Category</InputLabel>
          <Select
            value={selectedCategory}
            label="Category"
            onChange={(e) => setSelectedCategory(e.target.value as LogCategory | 'ALL')}
          >
            <MenuItem value="ALL">All Categories</MenuItem>
            {Object.values(LogCategory).map((category) => (
              <MenuItem key={category} value={category}>
                {category}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {filteredLogs.map((log, index) => (
          <LogEntry key={index} level={log.level}>
            <LogTimestamp>
              {new Date(log.timestamp).toLocaleTimeString()}
            </LogTimestamp>
            <LogMessage>
              {log.component && `[${log.component}] `}
              {log.message}
            </LogMessage>
            {log.details && (
              <LogDetails>
                {JSON.stringify(log.details, null, 2)}
              </LogDetails>
            )}
          </LogEntry>
        ))}
        <div ref={logsEndRef} />
      </Box>
    </DebugPanelContainer>
  );
};

export default DebugPanel;
