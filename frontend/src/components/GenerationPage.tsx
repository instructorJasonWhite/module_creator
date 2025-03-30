import React, { useState, useRef, useEffect } from 'react';
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
  Card,
  CardContent,
  Divider,
  Collapse,
  IconButton as MuiIconButton,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SettingsIcon from '@mui/icons-material/Settings';
import RefreshIcon from '@mui/icons-material/Refresh';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { api, config } from '../config';
import { logger, LogCategory } from '../utils/logger';
import { fetchAgents } from '../services/system';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import toast from 'react-hot-toast';

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
  format: string;
  metadata?: any;
  processing_info?: any;
  analysis?: {
    topics: string[];
    subtopics: Record<string, string[]>;
    key_concepts: string[];
    complexity: string;
    suggested_structure: string;
    prerequisites?: string[];
    dependencies?: string[];
  };
}

interface AnalysisResult {
  topics: string[];
  subtopics: { [key: string]: string[] };
  key_concepts: string[];
  complexity: string;
  suggested_structure: string;
  prerequisites: string[];
  dependencies: string[];
}

interface AnalysisResponse {
  status: string;
  analysis: AnalysisResult;
  outline_file: string;
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
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentAnalyzerContext, setDocumentAnalyzerContext] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set());
  const [outlineContent, setOutlineContent] = useState<string>("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  // Fetch document analyzer context on component mount
  useEffect(() => {
    const fetchDocumentAnalyzerContext = async () => {
      try {
        const agents = await fetchAgents();
        const documentAnalyzer = agents.find(agent => agent.name === 'Document Analyzer');
        if (documentAnalyzer?.contexts?.[0]?.context) {
          setDocumentAnalyzerContext(documentAnalyzer.contexts[0].context);
          logger.debug(LogCategory.API, 'Fetched document analyzer context', documentAnalyzer.contexts[0].context, 'GenerationPage');
        }
      } catch (error) {
        logger.error(LogCategory.ERROR, 'Failed to fetch document analyzer context', error, 'GenerationPage');
      }
    };

    fetchDocumentAnalyzerContext();
  }, []);

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
    try {
      setCurrentFile(file);
      setProcessingResult(null);
      setUploadProgress(0);
      setUploadError(null);
      setUploadSuccess(false);

      const formData = new FormData();
      formData.append("file", file);
      formData.append("original_filename", file.name);

      console.log("Uploading file:", file.name);

      // Add agent context if available
      if (documentAnalyzerContext) {
        formData.append('agent_context', documentAnalyzerContext);
        logger.debug(LogCategory.UPLOAD, 'Including agent context in upload', documentAnalyzerContext, 'GenerationPage');
      }

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
      setProcessingResult({
        ...response.data.data,
        processing_info: {
          ...response.data.data.processing_info,
          original_filename: file.name
        }
      });
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

  const handleTopicClick = (topic: string) => {
    setExpandedTopics(prev => {
      const newSet = new Set(prev);
      if (newSet.has(topic)) {
        newSet.delete(topic);
      } else {
        newSet.add(topic);
      }
      return newSet;
    });
  };

  const handleRegenerateAnalysis = async () => {
    if (!processingResult?.text || !processingResult?.format) {
      setAnalysisError('No document text or format available');
      return;
    }

    try {
      setIsAnalyzing(true);
      setAnalysisError(null);

      const formData = new FormData();
      formData.append('document_text', processingResult.text);
      formData.append('document_type', processingResult.format);
      if (documentAnalyzerContext) {
        formData.append('agent_context', documentAnalyzerContext);
      }

      logger.debug(LogCategory.API, 'Sending document analysis request', {
        documentType: processingResult.format,
        textLength: processingResult.text.length,
        hasContext: !!documentAnalyzerContext
      }, 'GenerationPage');

      const response = await axios.post(
        `${config.api.baseUrl}${config.api.endpoints.agents.analyze}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const progress = (progressEvent.loaded / (progressEvent.total || 1)) * 100;
            setUploadProgress(progress);
            logger.debug(LogCategory.UPLOAD, `Upload progress: ${Math.round(progress)}%`, null, 'GenerationPage');
          },
        }
      );

      if (response.data.status === 'success') {
        logger.info(LogCategory.API, 'Document analysis completed successfully', response.data, 'GenerationPage');
        setProcessingResult(prev => prev ? {
          ...prev,
          analysis: response.data.analysis
        } : null);
      } else {
        const errorMsg = response.data.error || 'Failed to analyze document';
        logger.error(LogCategory.ERROR, 'Document analysis failed', {
          error: errorMsg,
          response: response.data
        }, 'GenerationPage');
        setAnalysisError(`Analysis failed: ${errorMsg}`);
      }
    } catch (error) {
      const errorDetails = error instanceof Error ? {
        message: error.message,
        stack: error.stack,
        response: (error as any).response?.data
      } : 'Unknown error';

      logger.error(LogCategory.ERROR, 'Error analyzing document', errorDetails, 'GenerationPage');

      let errorMessage = 'Failed to analyze document';
      if (axios.isAxiosError(error)) {
        if (error.response) {
          errorMessage = `Server error: ${error.response.data.detail || error.response.statusText}`;
        } else if (error.request) {
          errorMessage = 'No response received from server. Please check your connection.';
        } else {
          errorMessage = `Request error: ${error.message}`;
        }
      }

      setAnalysisError(errorMessage);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDeployAgent = async () => {
    try {
      if (!processingResult?.text) {
        toast.error("Please upload and process a document first");
        return;
      }

      setIsAnalyzing(true);
      setAnalysisError(null);

      const formData = new FormData();
      formData.append("document_text", processingResult.text);
      formData.append("document_type", processingResult.format || "educational");
      formData.append("original_filename", currentFile?.name || "");

      const response = await api.post("/api/v1/agents/analyze", formData);
      setProcessingResult(prev => prev ? {
        ...prev,
        analysis: response.data.analysis
      } : null);

      if (response.data.outline_file) {
        try {
          const outlineResponse = await api.get(
            `/api/v1/documents/outline/${encodeURIComponent(response.data.outline_file)}`
          );
          setOutlineContent(outlineResponse.data);
        } catch (error) {
          console.error("Error fetching outline:", error);
          toast.error("Failed to fetch outline content");
        }
      }

      toast.success("Document analysis completed successfully");
    } catch (error) {
      console.error("Error deploying agent:", error);
      toast.error("Failed to analyze document");
    } finally {
      setIsAnalyzing(false);
    }
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
                    {processingResult?.format?.toUpperCase() || 'Unknown'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Pages
                  </Typography>
                  <Typography variant="body1">
                    {processingResult?.processing_info?.pages || 'Unknown'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Characters
                  </Typography>
                  <Typography variant="body1">
                    {processingResult?.text?.length?.toLocaleString() || '0'}
                  </Typography>
                </Grid>
                {processingResult?.processing_info?.is_scanned && (
                  <Grid item xs={12}>
                    <Alert severity="warning" sx={{ mt: 1 }}>
                      This appears to be a scanned document
                    </Alert>
                  </Grid>
                )}
                {processingResult?.processing_info?.ocr_used && (
                  <Grid item xs={12}>
                    <Alert severity="info" sx={{ mt: 1 }}>
                      OCR was used to extract text
                    </Alert>
                  </Grid>
                )}
              </Grid>
            </Paper>

            {/* Document Preview */}
            {processingResult?.text && (
              <Paper sx={{ p: 2, mb: 2, maxHeight: '300px', overflow: 'auto' }}>
                <Typography variant="h6" gutterBottom>
                  Document Preview
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {processingResult.text.substring(0, 1000)}...
                </Typography>
              </Paper>
            )}

            {/* Deploy Agent Button */}
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', mb: 3 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleDeployAgent}
                disabled={isAnalyzing}
                startIcon={isAnalyzing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
              >
                {isAnalyzing ? 'Analyzing...' : 'Deploy Document Analyzer Agent'}
              </Button>
            </Box>

            {analysisError && (
              <Alert
                severity="error"
                sx={{
                  mb: 3,
                  '& .MuiAlert-message': {
                    width: '100%'
                  }
                }}
              >
                <Typography variant="subtitle1" gutterBottom>
                  Document Analysis Failed
                </Typography>
                <Typography variant="body2" component="div">
                  {analysisError}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Please try the following:
                  </Typography>
                  <ul style={{ margin: '8px 0 0 20px', padding: 0 }}>
                    <li>Check if the document is properly uploaded and readable</li>
                    <li>Verify your internet connection</li>
                    <li>Try regenerating the analysis</li>
                    <li>Contact support if the issue persists</li>
                  </ul>
                </Box>
              </Alert>
            )}

            {/* Analysis Results */}
            {isAnalyzing ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : processingResult?.analysis && processingResult.analysis.topics ? (
              <Card sx={{ mt: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Document Analysis
                    </Typography>
                    <MuiIconButton onClick={handleRegenerateAnalysis} color="primary">
                      <RefreshIcon />
                    </MuiIconButton>
                  </Box>
                  <Divider sx={{ my: 2 }} />

                  {/* Topics with Expandable Subtopics */}
                  <List>
                    {processingResult?.analysis?.topics?.map((topic: string, index: number) => (
                      <React.Fragment key={index}>
                        <ListItem
                          button
                          onClick={() => handleTopicClick(topic)}
                          sx={{
                            backgroundColor: expandedTopics.has(topic) ? 'action.hover' : 'transparent',
                            borderRadius: 1,
                            mb: 1
                          }}
                        >
                          <ListItemText
                            primary={topic}
                            secondary={`${processingResult?.analysis?.subtopics?.[topic]?.length || 0} subtopics`}
                          />
                          {expandedTopics.has(topic) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </ListItem>
                        <Collapse in={expandedTopics.has(topic)} timeout="auto" unmountOnExit>
                          <List component="div" disablePadding>
                            {processingResult?.analysis?.subtopics?.[topic]?.map((subtopic: string, subIndex: number) => (
                              <ListItem key={subIndex} sx={{ pl: 4 }}>
                                <ListItemText primary={subtopic} />
                              </ListItem>
                            ))}
                          </List>
                        </Collapse>
                      </React.Fragment>
                    ))}
                  </List>

                  {/* Key Concepts */}
                  <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                    Key Concepts:
                  </Typography>
                  <List>
                    {processingResult.analysis.key_concepts.map((concept: string, index: number) => (
                      <ListItem key={index}>
                        <ListItemText primary={concept} />
                      </ListItem>
                    ))}
                  </List>

                  {/* Complexity */}
                  <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                    Complexity Level:
                  </Typography>
                  <Typography variant="body1" sx={{ ml: 2 }}>
                    {processingResult.analysis.complexity}
                  </Typography>

                  {/* Suggested Structure */}
                  <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                    Suggested Structure:
                  </Typography>
                  <Typography variant="body1" sx={{ ml: 2 }}>
                    {processingResult.analysis.suggested_structure}
                  </Typography>

                  {/* Prerequisites */}
                  {processingResult.analysis.prerequisites && processingResult.analysis.prerequisites.length > 0 && (
                    <>
                      <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                        Prerequisites:
                      </Typography>
                      <List>
                        {processingResult.analysis.prerequisites.map((prereq: string, index: number) => (
                          <ListItem key={index}>
                            <ListItemText primary={prereq} />
                          </ListItem>
                        ))}
                      </List>
                    </>
                  )}

                  {/* Dependencies */}
                  {processingResult.analysis.dependencies && processingResult.analysis.dependencies.length > 0 && (
                    <>
                      <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                        Dependencies:
                      </Typography>
                      <List>
                        {processingResult.analysis.dependencies.map((dep: string, index: number) => (
                          <ListItem key={index}>
                            <ListItemText primary={dep} />
                          </ListItem>
                        ))}
                      </List>
                    </>
                  )}
                </CardContent>
              </Card>
            ) : null}

            {/* Outline Section */}
            {outlineContent && (
              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Outline
                </Typography>
                <Paper sx={{ p: 2, maxHeight: 400, overflow: "auto" }}>
                  <Typography variant="body1" component="pre" sx={{ whiteSpace: "pre-wrap" }}>
                    {outlineContent}
                  </Typography>
                </Paper>
              </Box>
            )}
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
