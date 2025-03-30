import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Container,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  CircularProgress,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { logger, LogCategory } from '../utils/logger';

const GenerationContainer = styled(Container)(({ theme }) => ({
  padding: theme.spacing(4),
  background: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(10px)',
  minHeight: '100vh',
}));

const GenerationCard = styled(Card)(({ theme }) => ({
  height: '100%',
  background: 'rgba(255, 255, 255, 0.8)',
  backdropFilter: 'blur(5px)',
  transition: 'transform 0.2s',
  '&:hover': {
    transform: 'translateY(-4px)',
  },
}));

const GenerationPage: React.FC = () => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: Implement generation logic
      logger.info(LogCategory.API, 'Starting generation process', null, 'GenerationPage');
      // Add your generation logic here
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start generation';
      setError(errorMessage);
      logger.error(LogCategory.ERROR, errorMessage, error, 'GenerationPage');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <GenerationContainer maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Module Generation
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Configure and generate your learning module
        </Typography>
      </Box>

      {error && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'error.light' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <GenerationCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Module Configuration
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Module Description"
                placeholder="Describe your learning module..."
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Learning Objectives"
                placeholder="List the key learning objectives..."
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Target Audience"
                placeholder="Describe your target audience..."
                sx={{ mb: 2 }}
              />
              <Button
                variant="contained"
                color="primary"
                size="large"
                fullWidth
                onClick={handleGenerate}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <CircularProgress size={24} sx={{ mr: 1 }} />
                    Generating...
                  </>
                ) : (
                  'Generate Module'
                )}
              </Button>
            </CardContent>
          </GenerationCard>
        </Grid>

        <Grid item xs={12} md={4}>
          <GenerationCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Generation Status
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Ready to generate your learning module. Fill in the configuration details and click generate to begin the process.
              </Typography>
            </CardContent>
          </GenerationCard>
        </Grid>
      </Grid>
    </GenerationContainer>
  );
};

export default GenerationPage; 