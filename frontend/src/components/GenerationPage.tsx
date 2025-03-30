import React, { useState, useRef } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Stepper,
  Step,
  StepLabel,
  Container,
  Button,
  Grid,
  IconButton,
  Tooltip,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SettingsIcon from '@mui/icons-material/Settings';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { config } from '../config';
import { logger, LogCategory } from '../utils/logger';

// Styled components
const UploadArea = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  border: `2px dashed ${theme.palette.primary.main}`,
  backgroundColor: theme.palette.background.default,
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const TabPanel = (props: any) => {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`generation-tabpanel-${index}`}
      aria-labelledby={`generation-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

interface ProcessingResult {
  text: string;
  metadata: any;
  format: string;
  processing_info: any;
}

const MAX_FILE_SIZE = config.upload.maxFileSize;

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const steps = [
  'Upload Document',
  'Analyze Document',
  'User Preferences',
  'Module Design',
  'Preview & Approve',
  'Download'
];

const GenerationPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentStep(newValue);
  };

  const handleNewUpload = () => {
    setUploadSuccess(false);
    setProcessingResult(null);
    setCurrentStep(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  const validateFile = (file: File): string | null => {
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds maximum limit of ${formatFileSize(MAX_FILE_SIZE)}`;
    }
    return null;
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const error = validateFile(file);
    if (error) {
      setUploadError(error);
      return;
    }

    await uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    logger.debug(LogCategory.UPLOAD, `Starting file upload: ${file.name}`, null, 'GenerationPage');
    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(false);
    setProcessingResult(null);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      logger.debug(LogCategory.UPLOAD, `Sending request to ${config.api.baseUrl}${config.api.endpoints.documents.upload}`, null, 'GenerationPage');

      const response = await axios.post(`${config.api.baseUrl}${config.api.endpoints.documents.upload}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = (progressEvent.loaded / (progressEvent.total || 1)) * 100;
          setUploadProgress(progress);
          logger.debug(LogCategory.UPLOAD, `Upload progress: ${Math.round(progress)}%`, null, 'GenerationPage');
        },
      });

      logger.debug(LogCategory.UPLOAD, 'File uploaded successfully', response.data, 'GenerationPage');
      setProcessingResult(response.data.data);
      setUploadSuccess(true);

      // Move to the next step after successful upload
      setCurrentStep(1);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload file';
      logger.error(LogCategory.ERROR, `File upload failed: ${errorMessage}`, error, 'GenerationPage');
      setUploadError(errorMessage);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
  };

  const handleDrop = async (event: React.DragEvent) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (!file) return;

    const error = validateFile(file);
    if (error) {
      setUploadError(error);
      return;
    }

    await uploadFile(file);
  };

  const handleAdminClick = () => {
    logger.info(LogCategory.UI, 'Navigating to admin panel', null, 'GenerationPage');
    navigate('/admin');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ position: 'fixed', top: 16, left: 16, zIndex: 1000 }}>
        <Tooltip title="Admin Panel">
          <IconButton
            onClick={handleAdminClick}
            sx={{
              backgroundColor: 'background.paper',
              boxShadow: 1,
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <SettingsIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Paper sx={{ mb: 4, p: 3 }}>
        <Stepper activeStep={currentStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={currentStep}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          aria-label="generation steps"
        >
          {steps.map((label) => (
            <Tab key={label} label={label} />
          ))}
        </Tabs>
      </Paper>

      <TabPanel value={currentStep} index={0}>
        <label htmlFor="file-upload">
          <UploadArea
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <input
              id="file-upload"
              ref={fileInputRef}
              type="file"
              hidden
              onChange={handleFileUpload}
              accept=".pdf,.docx,.doc,.txt,.html,.htm,.png,.jpg,.jpeg,.tiff"
            />
            {isUploading ? (
              <Box sx={{ width: '100%' }}>
                <CircularProgress />
                <LinearProgress variant="determinate" value={uploadProgress} sx={{ mt: 2 }} />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Uploading... {Math.round(uploadProgress)}%
                </Typography>
              </Box>
            ) : uploadSuccess ? (
              <Alert severity="success">File uploaded successfully!</Alert>
            ) : (
              <>
                <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Drag and drop your document here
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  or click to select a file
                </Typography>
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Supported formats: PDF, DOCX, DOC, TXT, HTML, PNG, JPG, TIFF
                </Typography>
                <Typography variant="caption" display="block" color="text.secondary">
                  Maximum file size: {formatFileSize(MAX_FILE_SIZE)}
                </Typography>
              </>
            )}
            {uploadError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {uploadError}
              </Alert>
            )}
          </UploadArea>
        </label>
        {uploadSuccess && (
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="outlined"
              color="primary"
              onClick={handleNewUpload}
              startIcon={<CloudUploadIcon />}
            >
              Upload New Document
            </Button>
          </Box>
        )}
      </TabPanel>

      <TabPanel value={currentStep} index={1}>
        {processingResult ? (
          <Box>
            <Paper sx={{ p: 2, mb: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Format
                  </Typography>
                  <Typography variant="body1">
                    {processingResult.format.toUpperCase()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Pages
                  </Typography>
                  <Typography variant="body1">
                    {processingResult.processing_info.pages}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Characters
                  </Typography>
                  <Typography variant="body1">
                    {processingResult.text.length.toLocaleString()}
                  </Typography>
                </Grid>
                {processingResult.processing_info.is_scanned && (
                  <Grid item xs={12}>
                    <Alert severity="warning" sx={{ mt: 1 }}>
                      This appears to be a scanned document
                    </Alert>
                  </Grid>
                )}
                {processingResult.processing_info.ocr_used && (
                  <Grid item xs={12}>
                    <Alert severity="info" sx={{ mt: 1 }}>
                      OCR was used to extract text
                    </Alert>
                  </Grid>
                )}
              </Grid>
            </Paper>

            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Document Content
                </Typography>
              </Box>
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  height: '500px',
                  overflow: 'auto',
                  backgroundColor: 'grey.50',
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  lineHeight: 1.5,
                  '&::-webkit-scrollbar': {
                    width: '8px',
                  },
                  '&::-webkit-scrollbar-track': {
                    background: 'grey.200',
                  },
                  '&::-webkit-scrollbar-thumb': {
                    background: 'grey.400',
                    borderRadius: '4px',
                  },
                  '&::-webkit-scrollbar-thumb:hover': {
                    background: 'grey.500',
                  },
                }}
              >
                <Typography
                  component="pre"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    margin: 0,
                    padding: 0,
                  }}
                >
                  {processingResult.text}
                </Typography>
              </Paper>
            </Paper>
          </Box>
        ) : (
          <Typography>Please upload a document first</Typography>
        )}
      </TabPanel>

      <TabPanel value={currentStep} index={2}>
        <Typography>User Preferences Step</Typography>
        {/* TODO: Implement user preferences UI */}
      </TabPanel>

      <TabPanel value={currentStep} index={3}>
        <Typography>Module Design Step</Typography>
        {/* TODO: Implement module design UI */}
      </TabPanel>

      <TabPanel value={currentStep} index={4}>
        <Typography>Preview & Approval Step</Typography>
        {/* TODO: Implement preview and approval UI */}
      </TabPanel>

      <TabPanel value={currentStep} index={5}>
        <Typography>Download Step</Typography>
        {/* TODO: Implement download UI */}
      </TabPanel>
    </Container>
  );
};

export default GenerationPage;
