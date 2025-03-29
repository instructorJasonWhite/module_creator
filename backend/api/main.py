import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles

from ..core.config import settings
from ..core.file_storage import FileStorage
from ..core.rate_limit import RateLimiter
from ..core.security import (create_access_token, get_password_hash,
                             verify_password, verify_token)
from ..schemas.api_schemas import (APIKey, APIKeyCreate, ErrorResponse,
                                   FileInfo, FileUpload, PaginatedResponse,
                                   PaginationParams, RateLimit, RateLimitInfo,
                                   SuccessResponse, Token, TokenData, User,
                                   UserCreate, UserUpdate)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Educational Content Generator API",
    description="API for generating interactive educational content from documents",
    version="1.0.0",
)

# Initialize rate limiter
rate_limiter = RateLimiter(
    requests_per_minute=settings.RATE_LIMIT_REQUESTS,
    burst_size=settings.RATE_LIMIT_BURST,
)

# Initialize file storage
file_storage = FileStorage(
    upload_dir=settings.UPLOAD_DIR,
    allowed_types=settings.ALLOWED_FILE_TYPES,
    max_file_size=settings.MAX_FILE_SIZE,
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Middleware for request logging and rate limiting
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Check rate limit
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Too many requests",
                "code": "RATE_LIMIT_EXCEEDED",
                "details": {"reset": rate_limiter.get_reset_time(client_ip)},
            },
        )

    response = await call_next(request)

    # Log request
    process_time = time.time() - start_time
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Time: {process_time:.3f}s"
    )

    return response


# Error handling middleware
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail, code=f"HTTP_{exc.status_code}", details=exc.detail
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            code="INTERNAL_ERROR",
            details={"message": str(exc)},
        ).dict(),
    )


# Authentication dependencies
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        token_data = verify_token(token)
        # TODO: Get user from database
        return User(
            user_id=token_data.user_id,
            email=token_data.email,
            username="test_user",
            role=token_data.role,
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# API routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # TODO: Verify user credentials against database
    user = User(
        user_id=uuid4(),
        email=form_data.username,
        username=form_data.username,
        role=UserRole.GUEST,
    )

    access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email, "role": user.role}
    )

    return Token(
        access_token=access_token,
        expires_at=datetime.utcnow()
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


@app.post("/users", response_model=User)
async def create_user(
    user: UserCreate, current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # TODO: Create user in database
    return User(
        user_id=uuid4(), email=user.email, username=user.username, role=user.role
    )


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.post("/api-keys", response_model=APIKey)
async def create_api_key(
    api_key: APIKeyCreate, current_user: User = Depends(get_current_active_user)
):
    # TODO: Create API key in database
    return APIKey(
        key_id=uuid4(), user_id=current_user.user_id, key="test_key", name=api_key.name
    )


@app.post("/upload", response_model=FileInfo)
async def upload_file(
    file: UploadFile, current_user: User = Depends(get_current_active_user)
):
    try:
        file_info = await file_storage.save_file(file, current_user.user_id)
        return file_info
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/files", response_model=PaginatedResponse)
async def list_files(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: Get files from database with pagination
    return PaginatedResponse(
        items=[],
        total=0,
        page=pagination.page,
        size=pagination.size,
        pages=0,
        has_next=False,
        has_prev=False,
    )


@app.get("/rate-limit", response_model=RateLimitInfo)
async def get_rate_limit_info(request: Request):
    client_ip = request.client.host
    return rate_limiter.get_info(client_ip)


# Health check endpoint
@app.get("/health")
async def health_check():
    return SuccessResponse(
        message="Service is healthy",
        data={"timestamp": datetime.utcnow().isoformat(), "version": app.version},
    )
