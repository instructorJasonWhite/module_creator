# AI-Powered Educational Content Generator

## Project Overview
This project implements an agent-based system for transforming educational documents into interactive learning experiences. The system uses specialized AI agents to analyze, structure, and generate content, ultimately producing a single, self-contained HTML file that includes all necessary CSS and JavaScript. This modular approach allows for easy customization and enhancement of individual components while maintaining a cohesive workflow.

## Key Features

### Output Format
- **Single-File HTML Output**: All content, styles, and interactivity are embedded in one HTML file
- **Self-Contained**: No external dependencies required for viewing
- **Portable**: Can be shared and viewed on any device with a web browser
- **Interactive Elements**: All interactive components are embedded and functional without server connection
- **Preview & Download**: Built-in preview functionality and one-click download option

### Core Agents

1. **Document Analysis Agent**
   - Role: Analyzes uploaded documents and extracts key information
   - Responsibilities:
     - Document structure analysis
     - Topic identification
     - Key concept extraction
     - Content complexity assessment
   - Input: Raw documents (PDF, DOCX)
   - Output: Structured content analysis

2. **Module Planning Agent**
   - Role: Designs the learning module structure
   - Responsibilities:
     - Module organization
     - Content chunking
     - Learning path optimization
     - Prerequisites identification
   - Input: Document analysis results
   - Output: Module structure and organization plan

3. **Content Generation Agent**
   - Role: Creates the actual learning content
   - Responsibilities:
     - Content writing
     - Example generation
     - Visual content suggestions
     - Interactive element design
   - Input: Module structure and original content
   - Output: Generated learning modules

4. **Quiz Generation Agent**
   - Role: Creates assessments and quizzes
   - Responsibilities:
     - Question generation
     - Answer validation
     - Explanation creation
     - Difficulty calibration
   - Input: Learning module content
   - Output: Interactive quizzes and assessments

5. **Interactive Content Agent**
   - Role: Enhances content with interactive elements
   - Responsibilities:
     - UI component selection
     - Interactive element placement
     - User experience optimization
     - Responsive design implementation
   - Input: Generated content
   - Output: Interactive learning experience

### AI Model Integration
The system supports multiple AI model providers through a flexible agent architecture:

1. **OpenAI Integration**
   - Supports GPT models through OpenAI's API
   - Secure API key management
   - Configurable model parameters
   - Robust error handling
   - Context-aware message management

2. **Ollama Integration**
   - Local model support through Ollama
   - Custom model deployment
   - Configurable model parameters
   - Error handling and retries
   - Context management

3. **Model Management**
   - Centralized model configuration
   - Provider-specific settings
   - Model validation and health checks
   - Performance monitoring
   - Fallback mechanisms

4. **Agent Factory**
   - Dynamic agent creation
   - Provider-specific agent types
   - Configuration validation
   - Health monitoring
   - Load balancing

### Agent Communication

- Agents communicate through a structured message passing system
- Each agent maintains its own state and context
- Agents can request information from other agents as needed
- Workflow orchestration is handled by a central coordinator

## Technical Implementation

### Backend Architecture
- FastAPI-based API server
- Agent-specific microservices
- Redis for inter-agent communication
- PostgreSQL for persistent storage

### Agent Implementation
- Each agent is implemented as an independent service
- Agents use LangChain for prompt management
- Custom prompt templates for each agent's specific role
- Configurable agent parameters and behaviors

### Frontend Architecture
- React with TypeScript
- Material-UI components
- Real-time agent status monitoring
- Interactive content preview
- Single-file HTML generation system

### Output Generation
- **HTML Bundling**: Combines all content, styles, and scripts into a single file
- **Asset Management**: Embeds images, fonts, and other resources
- **Code Optimization**: Minifies and optimizes embedded code
- **Browser Compatibility**: Ensures cross-browser compatibility
- **File Size Optimization**: Balances functionality with file size

### AI Model Integration
- Provider-agnostic agent architecture
- Configurable model settings
- Secure API key management
- Robust error handling
- Performance monitoring
- Health checks and fallbacks

## Configuration

### Agent Configuration
Each agent can be configured through:
- Prompt templates
- Model parameters
- Behavior rules
- Output formats

### System Configuration
- Environment variables for API keys
- Agent communication settings
- Storage configurations
- Logging and monitoring settings
- Output customization options

## Development Setup

### Prerequisites

#### Windows
1. Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
2. Install Node.js and npm from [nodejs.org](https://nodejs.org/)
3. Install Git from [git-scm.com](https://git-scm.com/download/win)

#### Linux (Ubuntu/Debian)
1. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-dev python3-pip python3-venv nodejs npm git
   ```
2. For PDF processing support:
   ```bash
   sudo apt-get install libmupdf-dev
   ```
3. For PostgreSQL support:
   ```bash
   sudo apt-get install libpq-dev
   ```

### Project Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd module-creator
   ```

2. Verify the build environment:
   ```bash
   python verify_build.py
   ```
   This script will check:
   - Python version (3.8+ required)
   - Node.js version (16.x+ required)
   - Required files presence
   - Environment file setup
   - Dependency installation capability

3. Set up Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up frontend:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

6. Configure environment variables:
   ```bash
   # Windows
   copy .env.example .env

   # Linux
   cp .env.example .env
   ```
   Edit the `.env` file with your configuration values.

### Running the Application

1. Start the development servers:
   ```bash
   python run_dev.py
   ```
   This will start both the backend (FastAPI) and frontend (React) servers.

2. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Troubleshooting

#### Common Issues

1. **Port Conflicts**
   - If ports 3000 or 8000 are already in use, modify the ports in:
     - Frontend: `frontend/package.json` (proxy setting)
     - Backend: `backend/run.py`

2. **Python Dependencies**
   - If you encounter build errors for `psycopg2-binary`:
     - Windows: No additional steps needed
     - Linux: Install PostgreSQL development files: `sudo apt-get install libpq-dev`

3. **PDF Processing Issues**
   - If PyMuPDF fails to install:
     - Windows: No additional steps needed
     - Linux: Install MuPDF development files: `sudo apt-get install libmupdf-dev`

4. **Node.js Version Conflicts**
   - The project is tested with Node.js 16.x and 18.x
   - If you encounter issues, try using Node Version Manager (nvm) to switch versions

5. **Database Connection**
   - Ensure PostgreSQL is running
   - Verify database credentials in `.env`
   - Check database migrations are up to date:
     ```bash
     alembic upgrade head
     ```

#### Getting Help

If you encounter issues:
1. Check the error messages in the terminal
2. Review the logs in the `logs` directory
3. Check the [Issues](https://github.com/yourusername/module-creator/issues) page
4. Create a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Node.js version (`node --version`)
   - Full error message
   - Steps to reproduce the issue

## Environment Variables
Required environment variables:
- `OPENAI_API_KEY`: API key for OpenAI services
- `REDIS_URL`: Redis connection string
- `DATABASE_URL`: PostgreSQL connection string
- Agent-specific configuration files

## Customization

### Prompt Engineering
The system is designed to be easily customizable through prompt engineering:
- Each agent has its own prompt template
- Templates can be modified without changing code
- Prompt versioning and A/B testing support

### Agent Behavior
- Agent behaviors can be modified through configuration
- New agents can be added to the pipeline
- Existing agents can be enhanced or replaced

### Output Customization
- Customizable HTML templates
- Configurable styling options
- Adjustable interactive components
- Custom branding and theming

## Future Enhancements
- Additional specialized agents
- Advanced agent collaboration patterns
- Enhanced monitoring and analytics
- A/B testing framework
- Performance optimization tools
- User feedback integration
- Additional output format support
- Advanced interactive component library

## Contributing
1. Fork the repository
2. Create feature branch
3. Implement changes
4. Update agent documentation
5. Create Pull Request

## License
MIT License

## Acknowledgments
- OpenAI for AI model services
- LangChain for agent framework
- FastAPI team for the web framework
- React and Material-UI communities

### Admin Interface
The application includes a secure admin interface for debugging and system monitoring:

1. **Access**
   - URL: `/admin/login`
   - Default credentials: admin/admin (change in production)

2. **Features**
   - **Performance Monitoring**
     - Real-time system statistics
     - Agent status monitoring
     - Resource usage tracking
     - Performance graphs and analytics
     - Alert threshold configuration

   - **Debugging Tools**
     - Log level controls
     - Log filtering and search
     - Log export functionality
     - System diagnostics
     - Debug mode toggle

   - **Storage Management**
     - File storage monitoring
     - Storage cleanup tools
     - Storage analytics
     - Quota management
     - Backup controls

   - **Security Settings**
     - User management
     - Role-based access control
     - Access logs
     - Security audit tools
     - API key management

3. **Security**
   - JWT-based authentication
   - Role-based access control
   - Secure password hashing
   - Session management
   - Audit logging

4. **Usage**
   - Monitor system health
   - Debug issues
   - Manage storage
   - Configure security
   - View system logs

# Module Creator

A tool for creating educational modules from documents using AI agents.

## Generation Process Steps

The module generation process follows these steps:

1. **Document Upload (Step 0)**
   - Drag and drop or file upload interface
   - Supports common document formats (PDF, DOCX, TXT)
   - Visual feedback on successful upload
   - File validation and size checks

2. **Document Analysis (Step 1)**
   - Document Analyzer agent processes the uploaded file
   - Extracts key information and structure
   - Displays analysis results for user review
   - Progress indicator during analysis

3. **User Preferences (Step 2)**
   - Learning objectives input
   - Target audience selection
   - Difficulty level setting
   - Duration preferences
   - Visual style preferences

4. **Module Design (Step 3)**
   - Module Planner agent creates structure
   - Content Generator creates materials
   - Quiz Generator creates assessments
   - Quality Assurance reviews content
   - Progress tracking for each agent

5. **Preview & Approval (Step 4)**
   - Preview generated module
   - Review content quality
   - Check learning objectives alignment
   - Request revisions if needed
   - Final approval step

6. **Download (Step 5)**
   - Export options (HTML, PDF)
   - Download generated module
   - Save to user's library
   - Share options

## Project Structure
