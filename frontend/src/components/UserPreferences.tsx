import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Button,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  CircularProgress,
  Paper,
  Divider,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { useSnackbar } from 'notistack';
import { api, config } from '../config';
import { logger, LogCategory } from '../utils/logger';
import { AxiosError } from 'axios';

interface ModulePreferences {
  module_index: number;
  format: 'tabs' | 'accordions' | 'flashcards' | 'video' | 'text';
  include_quiz: boolean;
  quiz_type?: string;
  include_knowledge_check: boolean;
  knowledge_check_type?: string;
  settings?: Record<string, any>;
}

interface UserPreferences {
  number_of_modules: number;
  theme_prompt?: string;
  module_preferences: ModulePreferences[];
}

interface UserPreferencesProps {
  outlineContent?: string;
}

const defaultModulePreferences: ModulePreferences = {
  module_index: 0,
  format: 'tabs',
  include_quiz: true,
  include_knowledge_check: true,
};

const UserPreferences: React.FC<UserPreferencesProps> = ({ outlineContent }) => {
  const [preferences, setPreferences] = useState<UserPreferences>({
    number_of_modules: 5,
    module_preferences: [],
  });
  const [expandedModule, setExpandedModule] = useState<number | false>(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setIsLoading(true);
      logger.debug(LogCategory.API, 'Fetching user preferences', null, 'UserPreferences');
      const response = await api.get(config.api.endpoints.preferences.me);
      setPreferences(response.data);
      logger.debug(LogCategory.API, 'User preferences fetched successfully', response.data, 'UserPreferences');
    } catch (error) {
      const axiosError = error as AxiosError;
      if (axiosError.response?.status === 404) {
        // No preferences found, use defaults
        setPreferences({
          number_of_modules: 5,
          module_preferences: Array.from({ length: 5 }, (_, index) => ({
            ...defaultModulePreferences,
            module_index: index,
          })),
        });
        logger.debug(LogCategory.API, 'No preferences found, using defaults', null, 'UserPreferences');
      } else {
        logger.error(LogCategory.ERROR, 'Failed to fetch preferences', error, 'UserPreferences');
        enqueueSnackbar('Failed to load preferences', { variant: 'error' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      logger.debug(LogCategory.API, 'Saving user preferences', preferences, 'UserPreferences');
      await api.put(config.api.endpoints.preferences.me, preferences);
      enqueueSnackbar('Preferences saved successfully', { variant: 'success' });
      logger.debug(LogCategory.API, 'User preferences saved successfully', null, 'UserPreferences');
    } catch (error) {
      logger.error(LogCategory.ERROR, 'Failed to save preferences', error, 'UserPreferences');
      enqueueSnackbar('Failed to save preferences', { variant: 'error' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleModuleCountChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newCount = Math.max(1, Math.min(20, parseInt(event.target.value) || 1));
    setPreferences(prev => ({
      ...prev,
      number_of_modules: newCount,
      module_preferences: Array.from({ length: newCount }, (_, index) =>
        prev.module_preferences[index] || { ...defaultModulePreferences, module_index: index }
      ),
    }));
  };

  const handleModulePreferenceChange = (index: number, field: keyof ModulePreferences, value: any) => {
    setPreferences(prev => ({
      ...prev,
      module_preferences: prev.module_preferences.map((module, i) =>
        i === index ? { ...module, [field]: value } : module
      ),
    }));
  };

  const handleAccordionChange = (moduleIndex: number) => (
    event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpandedModule(isExpanded ? moduleIndex : false);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Preferences Panel */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                User Preferences
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Number of Modules"
                    type="number"
                    value={preferences.number_of_modules}
                    onChange={handleModuleCountChange}
                    inputProps={{ min: 1, max: 20 }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Theme Prompt"
                    multiline
                    rows={3}
                    value={preferences.theme_prompt || ''}
                    onChange={(e) => setPreferences(prev => ({ ...prev, theme_prompt: e.target.value }))}
                    placeholder="Enter custom theme prompt for HTML generation..."
                  />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Module Preferences
                  </Typography>
                  {preferences.module_preferences.map((module, index) => (
                    <Accordion
                      key={index}
                      expanded={expandedModule === index}
                      onChange={handleAccordionChange(index)}
                      sx={{ mb: 1 }}
                    >
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Module {index + 1}</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                              <InputLabel>Format</InputLabel>
                              <Select
                                value={module.format}
                                label="Format"
                                onChange={(e) => handleModulePreferenceChange(index, 'format', e.target.value)}
                              >
                                <MenuItem value="tabs">Tabs</MenuItem>
                                <MenuItem value="accordions">Accordions</MenuItem>
                                <MenuItem value="flashcards">Flashcards</MenuItem>
                                <MenuItem value="video">Video</MenuItem>
                                <MenuItem value="text">Text</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>

                          <Grid item xs={12} sm={6}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={module.include_quiz}
                                  onChange={(e) => handleModulePreferenceChange(index, 'include_quiz', e.target.checked)}
                                />
                              }
                              label="Include Quiz"
                            />
                          </Grid>

                          <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                              <InputLabel>Quiz Type</InputLabel>
                              <Select
                                value={module.quiz_type || ''}
                                label="Quiz Type"
                                onChange={(e) => handleModulePreferenceChange(index, 'quiz_type', e.target.value)}
                                disabled={!module.include_quiz}
                              >
                                <MenuItem value="multiple_choice">Multiple Choice</MenuItem>
                                <MenuItem value="true_false">True/False</MenuItem>
                                <MenuItem value="short_answer">Short Answer</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>

                          <Grid item xs={12} sm={6}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={module.include_knowledge_check}
                                  onChange={(e) => handleModulePreferenceChange(index, 'include_knowledge_check', e.target.checked)}
                                />
                              }
                              label="Include Knowledge Check"
                            />
                          </Grid>

                          <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                              <InputLabel>Knowledge Check Type</InputLabel>
                              <Select
                                value={module.knowledge_check_type || ''}
                                label="Knowledge Check Type"
                                onChange={(e) => handleModulePreferenceChange(index, 'knowledge_check_type', e.target.value)}
                                disabled={!module.include_knowledge_check}
                              >
                                <MenuItem value="short_answer">Short Answer</MenuItem>
                                <MenuItem value="matching">Matching</MenuItem>
                                <MenuItem value="fill_in_blank">Fill in the Blank</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                        </Grid>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Grid>
              </Grid>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSave}
                  disabled={isSaving}
                >
                  {isSaving ? <CircularProgress size={24} /> : 'Save Preferences'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Outline Panel */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Document Outline
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {outlineContent ? (
                <Paper
                  sx={{
                    p: 2,
                    maxHeight: 'calc(100vh - 300px)',
                    overflow: 'auto',
                    bgcolor: 'grey.50'
                  }}
                >
                  <Typography
                    component="pre"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'monospace',
                      fontSize: '0.875rem'
                    }}
                  >
                    {outlineContent}
                  </Typography>
                </Paper>
              ) : (
                <Typography color="text.secondary" align="center">
                  No outline available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserPreferences;
