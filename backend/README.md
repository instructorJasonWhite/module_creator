# Module Creator Backend

This is the backend service for the Module Creator application. It provides a FastAPI-based REST API with authentication, document analysis, and educational content generation capabilities.

## Features

- JWT-based authentication
- Document analysis and outline generation
- File upload and management
- User preferences management
- Educational content generation
- Comprehensive API documentation

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env` as needed

## Running the Server

To run the development server:

```bash
python run.py
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

The API uses JWT-based authentication. To authenticate:

1. Send a POST request to `/api/v1/auth/login` with:
   - username: "admin"
   - password: "admin"

2. Use the returned token in subsequent requests in the Authorization header:
   ```
   Authorization: Bearer <your_token>
   ```

## API Endpoints

### Document Analysis
- POST `/api/v1/agents/analyze` - Analyze uploaded documents
- GET `/api/v1/documents/outline/{filename}` - Retrieve generated outlines

### User Preferences
- GET `/api/v1/preferences/me` - Get current user preferences
- PUT `/api/v1/preferences/me` - Update user preferences

### System Management
- GET `/api/v1/system/agents` - List available agents
- GET `/api/v1/system/models` - List available models
- GET `/api/v1/system/health` - Check system health

## Development

- The server runs in development mode with hot reload enabled
- API endpoints are organized in the `app/api/v1/endpoints` directory
- Models and schemas are in their respective directories
- Configuration is managed through environment variables
- Code formatting is handled by black
- Type checking is performed by mypy
- Linting is done with flake8

## Recent Updates

- Fixed Pydantic model configuration issues
- Implemented document analysis functionality
- Added outline generation and retrieval
- Enhanced error handling for file operations
- Improved API documentation
- Added comprehensive logging system

## Project Structure

```
backend/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality
│   ├── crud/           # Database operations
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas
│   └── services/       # Business logic
├── tests/              # Test files
├── uploads/            # Uploaded files
└── outputs/           # Generated content
```
