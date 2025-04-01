import logging
import os

from app.db.logging import logger  # Import the logger
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Remove direct import of settings, use env variables directly
# from app.core.config import settings

load_dotenv()

# Use environment variable or default to SQLite
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./module_creator.db"  # Changed default db name
)

logger.info(f"Connecting to database: {SQLALCHEMY_DATABASE_URL}")

# Configure connect_args for SQLite
connect_args = (
    {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,  # Added connect_args
    pool_pre_ping=True,
    # Added pool settings from original config.py
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=True,  # Enable SQLAlchemy logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is moved to base_class.py
# Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        logger.debug("Creating new database session")
        yield db
    finally:
        logger.debug("Closing database session")
        db.close()
