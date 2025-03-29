import hashlib
import logging
import mimetypes
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID

import aiofiles
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)


class FileStorage:
    """File storage system for handling uploads and file management."""

    def __init__(
        self,
        upload_dir: str,
        allowed_types: List[str],
        max_file_size: int,
        chunk_size: int = 1024 * 1024,  # 1MB chunks
    ):
        """
        Initialize file storage.
        Args:
            upload_dir: Directory for file uploads
            allowed_types: List of allowed MIME types
            max_file_size: Maximum file size in bytes
            chunk_size: Size of chunks for file upload
        """
        self.upload_dir = Path(upload_dir)
        self.allowed_types = allowed_types
        self.max_file_size = max_file_size
        self.chunk_size = chunk_size

        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self, file: UploadFile, user_id: UUID, metadata: Optional[dict] = None
    ) -> dict:
        """
        Save an uploaded file.
        Args:
            file: Uploaded file
            user_id: User ID
            metadata: Additional file metadata
        Returns:
            dict: File information
        """
        # Validate file type
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(self.allowed_types)}",
            )

        # Generate unique filename
        file_hash = self._generate_file_hash(file.filename)
        extension = Path(file.filename).suffix
        filename = f"{file_hash}{extension}"

        # Create user directory
        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(exist_ok=True)

        # Save file
        file_path = user_dir / filename
        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                size = 0
                while chunk := await file.read(self.chunk_size):
                    if size + len(chunk) > self.max_file_size:
                        raise HTTPException(
                            status_code=400,
                            detail=f"File size exceeds maximum limit of {self.max_file_size} bytes",
                        )
                    await out_file.write(chunk)
                    size += len(chunk)
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail="Error saving file")

        # Get file information
        file_info = {
            "filename": filename,
            "original_name": file.filename,
            "content_type": file.content_type,
            "size": size,
            "path": str(file_path),
            "created_at": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "metadata": metadata or {},
        }

        return file_info

    def get_file_path(self, user_id: UUID, filename: str) -> Path:
        """
        Get the path of a file.
        Args:
            user_id: User ID
            filename: Filename
        Returns:
            Path: File path
        """
        return self.upload_dir / str(user_id) / filename

    def delete_file(self, user_id: UUID, filename: str) -> bool:
        """
        Delete a file.
        Args:
            user_id: User ID
            filename: Filename
        Returns:
            bool: True if file was deleted, False otherwise
        """
        file_path = self.get_file_path(user_id, filename)
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False

    def get_file_info(self, user_id: UUID, filename: str) -> Optional[dict]:
        """
        Get information about a file.
        Args:
            user_id: User ID
            filename: Filename
        Returns:
            Optional[dict]: File information
        """
        file_path = self.get_file_path(user_id, filename)
        if not file_path.exists():
            return None

        try:
            stat = file_path.stat()
            return {
                "filename": filename,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(file_path),
            }
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None

    def list_user_files(self, user_id: UUID) -> List[dict]:
        """
        List all files for a user.
        Args:
            user_id: User ID
        Returns:
            List[dict]: List of file information
        """
        user_dir = self.upload_dir / str(user_id)
        if not user_dir.exists():
            return []

        files = []
        try:
            for file_path in user_dir.iterdir():
                if file_path.is_file():
                    file_info = self.get_file_info(user_id, file_path.name)
                    if file_info:
                        files.append(file_info)
        except Exception as e:
            logger.error(f"Error listing user files: {str(e)}")

        return files

    def cleanup_old_files(self, max_age_days: int = 30) -> int:
        """
        Clean up files older than specified age.
        Args:
            max_age_days: Maximum age of files in days
        Returns:
            int: Number of files deleted
        """
        deleted_count = 0
        cutoff = datetime.utcnow().timestamp() - (max_age_days * 24 * 60 * 60)

        try:
            for user_dir in self.upload_dir.iterdir():
                if user_dir.is_dir():
                    for file_path in user_dir.iterdir():
                        if file_path.is_file():
                            if file_path.stat().st_mtime < cutoff:
                                file_path.unlink()
                                deleted_count += 1
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")

        return deleted_count

    def _generate_file_hash(self, filename: str) -> str:
        """Generate a unique hash for a filename."""
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{filename}{timestamp}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:16]

    def validate_file_type(self, content_type: str) -> bool:
        """Validate if a file type is allowed."""
        return content_type in self.allowed_types

    def validate_file_size(self, size: int) -> bool:
        """Validate if a file size is within limits."""
        return size <= self.max_file_size
