import logging
from typing import Dict, Optional

from app.agents.document_analyzer.agent import DocumentAnalyzerAgent
from app.core.config import settings
from fastapi import Request

logger = logging.getLogger(__name__)

_agent_instances: Dict[str, DocumentAnalyzerAgent] = {}


async def get_document_analyzer() -> DocumentAnalyzerAgent:
    """
    Get or create a DocumentAnalyzerAgent instance.
    Uses a singleton pattern to avoid creating multiple instances.
    """
    agent_key = "document_analyzer"

    if agent_key not in _agent_instances:
        logger.debug("Creating new DocumentAnalyzerAgent instance")
        try:
            agent = DocumentAnalyzerAgent(settings.DOCUMENT_ANALYZER_CONFIG)
            _agent_instances[agent_key] = agent
            logger.info("Successfully created DocumentAnalyzerAgent instance")
        except Exception as e:
            logger.error(
                f"Failed to create DocumentAnalyzerAgent: {str(e)}", exc_info=True
            )
            raise

    return _agent_instances[agent_key]
