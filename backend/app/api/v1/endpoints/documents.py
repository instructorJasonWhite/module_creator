import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from app.services.document_processor import DocumentProcessor
from app.core.config import settings
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize document processor
document_processor = DocumentProcessor()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and process a document
    
    Args:
        file: The uploaded file
        
    Returns:
        Dictionary containing processed document information
    """
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in document_processor.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {', '.join(document_processor.SUPPORTED_FORMATS.keys())}"
            )

        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save uploaded file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process the document
        result = await document_processor.process_document(str(file_path))

        # Clean up the uploaded file
        os.remove(file_path)

        return JSONResponse(
            content={
                "status": "success",
                "message": "Document processed successfully",
                "data": result
            }
        )

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        ) 