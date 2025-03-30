import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings
from app.services.document_processor import DocumentProcessor
from fastapi import APIRouter, File, HTTPException, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize document processor
document_processor = DocumentProcessor()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    agent_context: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Upload and process a document

    Args:
        file: The uploaded file
        agent_context: Optional context to be passed to the document analyzer agent

    Returns:
        Dictionary containing processed document information
    """
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in document_processor.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {', '.join(document_processor.SUPPORTED_FORMATS.keys())}",
            )

        # Validate file size
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )

        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save uploaded file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # Process the document with agent context
        result = await document_processor.process_document(str(file_path), agent_context)

        # Clean up the uploaded file
        os.remove(file_path)

        return JSONResponse(
            content={
                "status": "success",
                "message": "Document processed successfully",
                "data": result,
            }
        )

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )

@router.get("/outline/{filename}")
async def get_outline(filename: str):
    """Get the outline file content"""
    try:
        logger.debug(f"=== Starting Outline Retrieval ===")
        logger.debug(f"Requested filename: {filename}")
        
        # Decode the URL-encoded filename
        decoded_filename = os.path.basename(filename)
        logger.debug(f"Decoded filename: {decoded_filename}")
        
        # Get the project root directory (3 levels up from this file)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        outline_path = os.path.join(base_dir, "outputs", "outlines", decoded_filename)
        logger.debug(f"Looking for outline at path: {outline_path}")
        
        # Check if file exists
        if not os.path.exists(outline_path):
            logger.error(f"Outline file not found at path: {outline_path}")
            raise HTTPException(status_code=404, detail="Outline file not found")
        
        logger.debug(f"Found outline file, size: {os.path.getsize(outline_path)} bytes")
        
        # Read file content to verify it's accessible
        with open(outline_path, "r", encoding="utf-8") as f:
            content = f.read()
            logger.debug(f"Successfully read outline content, length: {len(content)} chars")
        
        # Return the file content
        logger.info(f"Successfully serving outline file: {decoded_filename}")
        return FileResponse(outline_path, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error serving outline file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
