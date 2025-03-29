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

1. Clone repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```
3. Configure environment variables
4. Start the agent services:
   ```bash
   python -m agents.document_analyzer
   python -m agents.module_planner
   python -m agents.content_generator
   python -m agents.quiz_generator
   python -m agents.interactive_content
   ```
5. Start the API server:
   ```bash
   uvicorn main:app --reload
   ```
6. Start the frontend:
   ```bash
   npm start
   ```

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
   - Default credentials:
     - Username: `admin`
     - Password: `admin`
   - Note: Change these credentials in production

2. **Features**
   - Performance monitoring
   - System statistics
   - Debug settings
   - Storage management
   - Security settings

3. **Debugging Tools**
   - Real-time system stats
   - Log level control
   - Verbose logging toggle
   - Mock data simulation
   - Slow response simulation

4. **Security**
   - Protected routes
   - Token-based authentication
   - Session management
   - Access logging
   - Secure credential handling
