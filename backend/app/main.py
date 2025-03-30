import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from .core.config import settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting FastAPI application...")
logger.debug(f"API V1 prefix: {settings.API_V1_STR}")
logger.debug(f"CORS origins: {settings.CORS_ORIGINS}")

app = FastAPI(
    title="Module Creator API", openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Use specific origins from settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include API router
logger.debug("Including API router...")
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    logger.debug(f"Current settings: {settings.dict()}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown...")

@app.get("/")
async def root():
    return {"message": "Welcome to Module Creator API"}
