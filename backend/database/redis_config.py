import os
from typing import Optional

import redis
from dotenv import load_dotenv
from rq import Queue

load_dotenv()

# Redis connection configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Create Redis connection pool
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
)


def get_redis_connection() -> redis.Redis:
    """Get a Redis connection from the pool."""
    return redis.Redis(connection_pool=redis_pool)


def get_queue(queue_name: str = "default") -> Queue:
    """Get a Redis Queue instance."""
    return Queue(queue_name, connection=get_redis_connection())


def check_redis_health() -> tuple[bool, Optional[str]]:
    """
    Check Redis connection health.
    Returns:
        tuple: (is_healthy: bool, error_message: Optional[str])
    """
    try:
        redis_conn = get_redis_connection()
        redis_conn.ping()
        return True, None
    except redis.ConnectionError as e:
        return False, f"Redis connection error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error checking Redis health: {str(e)}"


def retry_operation(func, max_retries: int = 3, retry_delay: int = 1):
    """
    Decorator for retrying Redis operations.
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    """

    def wrapper(*args, **kwargs):
        import time

        attempts = 0
        while attempts < max_retries:
            try:
                return func(*args, **kwargs)
            except (redis.ConnectionError, redis.TimeoutError) as e:
                attempts += 1
                if attempts == max_retries:
                    raise e
                time.sleep(retry_delay)

    return wrapper
