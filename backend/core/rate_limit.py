import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional


class RateLimiter:
    """Rate limiter implementation using token bucket algorithm."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        window_seconds: int = 60,
    ):
        """
        Initialize rate limiter.
        Args:
            requests_per_minute: Maximum number of requests allowed per minute
            burst_size: Maximum number of requests allowed in burst
            window_seconds: Time window in seconds
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.window_seconds = window_seconds

        # Token bucket for each client
        self.tokens: Dict[str, float] = defaultdict(lambda: burst_size)
        self.last_update: Dict[str, datetime] = defaultdict(lambda: datetime.utcnow())

        # Request history for each client
        self.request_history: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """
        Check if a request is allowed for the client.
        Args:
            client_id: Client identifier (e.g., IP address)
        Returns:
            bool: True if request is allowed, False otherwise
        """
        now = datetime.utcnow()

        # Clean up old request history
        self._cleanup_history(client_id, now)

        # Update token bucket
        self._update_tokens(client_id, now)

        # Check if request is allowed
        if self.tokens[client_id] >= 1:
            self.tokens[client_id] -= 1
            self.request_history[client_id].append(now)
            return True

        return False

    def get_info(self, client_id: str) -> Dict:
        """
        Get rate limit information for a client.
        Args:
            client_id: Client identifier
        Returns:
            Dict: Rate limit information
        """
        now = datetime.utcnow()

        # Clean up old request history
        self._cleanup_history(client_id, now)

        # Update token bucket
        self._update_tokens(client_id, now)

        # Calculate remaining requests
        remaining = int(self.tokens[client_id])
        used = len(self.request_history[client_id])

        # Calculate reset time
        if used > 0:
            oldest_request = self.request_history[client_id][0]
            reset = oldest_request + timedelta(seconds=self.window_seconds)
        else:
            reset = now

        return {
            "remaining": remaining,
            "reset": reset,
            "limit": self.requests_per_minute,
            "used": used,
        }

    def get_reset_time(self, client_id: str) -> datetime:
        """
        Get the time when the rate limit will reset.
        Args:
            client_id: Client identifier
        Returns:
            datetime: Reset time
        """
        if not self.request_history[client_id]:
            return datetime.utcnow()

        oldest_request = self.request_history[client_id][0]
        return oldest_request + timedelta(seconds=self.window_seconds)

    def _update_tokens(self, client_id: str, now: datetime):
        """Update token bucket for a client."""
        time_passed = (now - self.last_update[client_id]).total_seconds()
        tokens_to_add = time_passed * (self.requests_per_minute / 60)

        self.tokens[client_id] = min(
            self.burst_size, self.tokens[client_id] + tokens_to_add
        )
        self.last_update[client_id] = now

    def _cleanup_history(self, client_id: str, now: datetime):
        """Clean up old request history."""
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.request_history[client_id] = [
            t for t in self.request_history[client_id] if t > cutoff
        ]

    def reset(self, client_id: str):
        """Reset rate limit for a client."""
        self.tokens[client_id] = self.burst_size
        self.request_history[client_id] = []
        self.last_update[client_id] = datetime.utcnow()

    def get_client_stats(self, client_id: str) -> Dict:
        """
        Get statistics for a client.
        Args:
            client_id: Client identifier
        Returns:
            Dict: Client statistics
        """
        now = datetime.utcnow()
        self._cleanup_history(client_id, now)

        return {
            "total_requests": len(self.request_history[client_id]),
            "current_tokens": self.tokens[client_id],
            "last_request": self.request_history[client_id][-1]
            if self.request_history[client_id]
            else None,
            "reset_time": self.get_reset_time(client_id),
        }
