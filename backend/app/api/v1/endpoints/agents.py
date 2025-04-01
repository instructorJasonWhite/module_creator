import logging
from datetime import datetime
from typing import Any, Dict, Optional

from app.agents.document_analyzer.agent import DocumentAnalyzerAgent
from app.core.config import settings
from app.core.dependencies import get_document_analyzer
from app.services.document_processor import DocumentProcessor
from fastapi import APIRouter, Depends, Form, HTTPException

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@router.post("/analyze")
async def analyze_document(
    document_text: str = Form(...),
    document_type: str = Form(...),
    agent_context: Optional[str] = Form(None),
    original_filename: Optional[str] = Form(None),
    document_analyzer: DocumentAnalyzerAgent = Depends(get_document_analyzer),
) -> Dict[str, Any]:
    """
    Analyze a document using the document analyzer agent

    Args:
        document_text: The text content to analyze
        document_type: Type of document (e.g., "pdf", "docx")
        agent_context: Optional context to be passed to the agent
        original_filename: Original filename of the document
        document_analyzer: DocumentAnalyzerAgent instance (injected)

    Returns:
        Dictionary containing the analysis results
    """
    try:
        # Log incoming request details
        logger.info("=== Document Analysis Request Received ===")
        logger.info(f"Request received at: {datetime.now().isoformat()}")
        logger.info(f"Document type: {document_type}")
        logger.info(f"Document text length: {len(document_text)}")
        logger.info(f"Agent context provided: {bool(agent_context)}")
        logger.info(f"Original filename: {original_filename}")
        logger.info(f"Document text preview: {document_text[:200]}...")
        logger.info("========================================")

        # Validate input data
        logger.debug("Validating input data")
        if not document_text:
            logger.error("No document text provided in input data")
            raise HTTPException(status_code=400, detail="Document text is required")

        # Prepare input data for the agent
        input_data = {
            "document_text": document_text,
            "document_type": document_type,
            "agent_context": agent_context,
            "original_filename": original_filename,
        }
        logger.debug("Prepared input data for agent")

        # Process the document with the agent
        logger.info("Calling DocumentAnalyzerAgent.process()")
        result = await document_analyzer.process(input_data)
        logger.debug(f"Agent process result status: {result.get('status')}")

        if result.get("status") == "error":
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Agent returned error status: {error_msg}")
            raise HTTPException(
                status_code=500, detail=f"Error analyzing document: {error_msg}"
            )

        logger.info("Document analysis completed successfully")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in document analysis endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error analyzing document: {str(e)}"
        )
