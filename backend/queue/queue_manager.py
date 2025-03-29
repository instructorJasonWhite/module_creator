import json
from datetime import datetime
from typing import Any, Optional, Type
from uuid import UUID

from ..database.redis_config import (get_queue, get_redis_connection,
                                     retry_operation)
from ..schemas.message_schemas import (AgentResponse, AgentTask, BaseMessage,
                                       ContentGenerationRequest,
                                       ContentGenerationResponse)


class QueueManager:
    """Manages message queues and message processing."""

    QUEUE_TYPES = {
        "content_generation": ContentGenerationRequest,
        "agent_task": AgentTask,
        "response": ContentGenerationResponse,
        "agent_response": AgentResponse,
    }

    def __init__(self):
        self.redis = get_redis_connection()
        self.queues = {
            queue_type: get_queue(queue_type) for queue_type in self.QUEUE_TYPES
        }

    @retry_operation
    def enqueue_message(
        self, queue_type: str, message: BaseMessage, timeout: int = 3600
    ) -> UUID:
        """
        Enqueue a message to the specified queue.
        Args:
            queue_type: Type of queue to use
            message: Message to enqueue
            timeout: Job timeout in seconds
        Returns:
            UUID: Message ID
        """
        if queue_type not in self.QUEUE_TYPES:
            raise ValueError(f"Invalid queue type: {queue_type}")

        if not isinstance(message, self.QUEUE_TYPES[queue_type]):
            raise TypeError(
                f"Message must be of type {self.QUEUE_TYPES[queue_type].__name__}"
            )

        # Store message metadata
        message_data = message.model_dump()
        self.redis.hset(
            f"message:{message.message_id}",
            mapping={
                "data": json.dumps(message_data),
                "queue_type": queue_type,
                "status": "pending",
                "enqueued_at": datetime.utcnow().isoformat(),
            },
        )

        # Enqueue the job
        self.queues[queue_type].enqueue(
            "process_message",
            args=(message.message_id, message_data),
            job_timeout=timeout,
        )

        return message.message_id

    @retry_operation
    def get_message_status(self, message_id: UUID) -> Optional[dict[str, Any]]:
        """
        Get the status and metadata of a message.
        Args:
            message_id: UUID of the message
        Returns:
            Optional[dict]: Message metadata if found
        """
        message_key = f"message:{message_id}"
        message_data = self.redis.hgetall(message_key)

        if not message_data:
            return None

        message_data["data"] = json.loads(message_data["data"])
        return message_data

    @retry_operation
    def update_message_status(
        self, message_id: UUID, status: str, error: Optional[str] = None
    ) -> bool:
        """
        Update the status of a message.
        Args:
            message_id: UUID of the message
            status: New status
            error: Optional error message
        Returns:
            bool: True if update successful
        """
        message_key = f"message:{message_id}"
        if not self.redis.exists(message_key):
            return False

        update_data = {"status": status, "updated_at": datetime.utcnow().isoformat()}
        if error:
            update_data["error"] = error

        self.redis.hmset(message_key, update_data)
        return True

    def get_queue_stats(self) -> dict[str, dict[str, int]]:
        """
        Get statistics for all queues.
        Returns:
            dict: Queue statistics
        """
        stats = {}
        for queue_type, queue in self.queues.items():
            stats[queue_type] = {
                "queued": queue.count,
                "failed": queue.failed_job_registry.count,
                "started": queue.started_job_registry.count,
                "finished": queue.finished_job_registry.count,
            }
        return stats
