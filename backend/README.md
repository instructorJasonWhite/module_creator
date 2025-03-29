# Module Creator Backend

This is the backend service for the Module Creator application. It provides a FastAPI-based REST API with authentication and other necessary endpoints.

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

## Development

- The server runs in development mode with hot reload enabled
- API endpoints are organized in the `app/api/v1/endpoints` directory
- Models and schemas are in their respective directories
- Configuration is managed through environment variables
