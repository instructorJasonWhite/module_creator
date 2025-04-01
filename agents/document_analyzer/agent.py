import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from backend.app.core.config import settings
from backend.app.services.model_service import get_active_model
from backend.core.base_agent import AgentConfig, BaseAgent

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DocumentAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing educational documents"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the agent with configuration"""
        try:
            logger.debug(f"Initializing DocumentAnalyzerAgent with config: {config}")
            agent_config = AgentConfig(**config)
            super().__init__(agent_config)
            logger.info("Successfully initialized DocumentAnalyzerAgent")
        except Exception as e:
            logger.error(
                f"Failed to initialize DocumentAnalyzerAgent: {str(e)}", exc_info=True
            )
            raise

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input document and extract key information

        Args:
            input_data: Dictionary containing:
                - document_text: The text content to analyze
                - document_type: Type of document (e.g., "pdf", "docx")
                - metadata: Additional document metadata

        Returns:
            Dictionary containing:
                - topics: List of main topics
                - subtopics: Dictionary mapping topics to subtopics
                - key_concepts: List of key concepts
                - complexity: Complexity assessment
                - suggested_structure: Suggested module structure
        """
        try:
            # Validate input data
            logger.debug("Validating input data")
            if not input_data.get("document_text"):
                logger.error("No document text provided in input data")
                raise ValueError("No document text provided")
            if not input_data.get("document_type"):
                logger.error("No document type provided in input data")
                raise ValueError("No document type provided")

            # Get active model settings
            logger.debug("Fetching active model settings")
            active_model = await get_active_model()
            if not active_model:
                logger.error("No active model found in settings")
                raise ValueError("No active model found")
            logger.debug(f"Using active model: {active_model['model_name']}")

            # Update agent config with active model
            logger.debug("Updating agent config with active model settings")
            self.config.model_name = active_model["model_name"]
            self.config.temperature = active_model["temperature"]
            self.config.max_tokens = active_model["max_tokens"]

            # Get agent context
            context = input_data.get("agent_context", "")
            if context:
                logger.info(f"Using agent context: {context}")
            else:
                logger.debug("No agent context provided")

            # Format the prompt with input data and context
            logger.debug("Formatting prompt")
            messages = self._format_prompt(input_data, context)
            logger.debug(f"Generated {len(messages)} messages for LLM")

            # Execute the LLM
            logger.info(f"Executing LLM with model {self.config.model_name}")
            response = await self._execute_llm(messages)
            logger.debug(f"Received response of length {len(response)}")

            # Parse the response
            logger.debug("Parsing LLM response")
            analysis = self._parse_response(response)
            logger.debug(f"Parsed analysis contains {len(analysis)} fields")

            # Validate the output
            logger.debug("Validating analysis output")
            if not self._validate_output(analysis):
                logger.error("Invalid analysis output structure")
                raise ValueError("Invalid analysis output")
            logger.info("Analysis output validation successful")

            # Send results to module planner
            logger.debug("Sending results to module planner")
            await self.send_message(
                "module_planner", {"type": "document_analysis", "data": analysis}
            )
            logger.debug("Results sent to module planner")

            result = {
                "status": "success",
                "agent": self.config.name,
                "analysis": analysis,
                "model_used": self.config.model_name,
                "timestamp": datetime.now().isoformat(),
            }
            logger.info("Document analysis completed successfully")
            return result

        except Exception as e:
            logger.error(
                f"Error in DocumentAnalyzerAgent.process: {str(e)}", exc_info=True
            )
            return await self._handle_error(e)

    def _format_prompt(
        self, input_data: Dict[str, Any], context: str = ""
    ) -> List[Dict[str, str]]:
        """Format the prompt template with input data and context"""
        try:
            document_text = input_data.get("document_text", "")
            document_type = input_data.get("document_type", "")

            logger.debug(f"Formatting prompt for {document_type} document")
            logger.debug(f"Document text length: {len(document_text)}")
            logger.debug(f"Context provided: {bool(context)}")

            prompt = f"""You are an expert educational content analyzer. Your task is to analyze the provided {document_type} document and create a detailed outline of its content.

Please analyze the following document and provide:
1. Main topics and their hierarchy
2. Key concepts and their relationships
3. Content complexity assessment
4. Suggested module structure
5. Prerequisites and dependencies

Document Content:
{document_text}

Additional Context:
{context}

Please provide your analysis in a structured format."""

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert educational content analyzer.",
                },
                {"role": "user", "content": prompt},
            ]
            logger.debug(f"Generated prompt with {len(prompt)} characters")
            return messages
        except Exception as e:
            logger.error(f"Error formatting prompt: {str(e)}", exc_info=True)
            raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data"""
        try:
            logger.debug("Attempting to parse response as JSON")
            # Try to parse as JSON first
            return json.loads(response)
        except json.JSONDecodeError:
            logger.debug("Response is not JSON, parsing as text")
            # If not JSON, try to extract structured data from text
            analysis = {
                "topics": [],
                "subtopics": {},
                "key_concepts": [],
                "complexity": "",
                "suggested_structure": "",
                "prerequisites": [],
                "dependencies": [],
            }

            # Split response into sections
            sections = response.split("\n\n")
            logger.debug(f"Split response into {len(sections)} sections")

            for section in sections:
                try:
                    if "Topics:" in section:
                        topics = section.split("Topics:")[1].strip().split("\n")
                        analysis["topics"] = [
                            t.strip("- ") for t in topics if t.strip()
                        ]
                        logger.debug(f"Parsed {len(analysis['topics'])} topics")
                    elif "Key Concepts:" in section:
                        concepts = section.split("Key Concepts:")[1].strip().split("\n")
                        analysis["key_concepts"] = [
                            c.strip("- ") for c in concepts if c.strip()
                        ]
                        logger.debug(
                            f"Parsed {len(analysis['key_concepts'])} key concepts"
                        )
                    elif "Complexity:" in section:
                        analysis["complexity"] = section.split("Complexity:")[1].strip()
                        logger.debug("Parsed complexity")
                    elif "Structure:" in section:
                        analysis["suggested_structure"] = section.split("Structure:")[
                            1
                        ].strip()
                        logger.debug("Parsed structure")
                    elif "Prerequisites:" in section:
                        prereqs = section.split("Prerequisites:")[1].strip().split("\n")
                        analysis["prerequisites"] = [
                            p.strip("- ") for p in prereqs if p.strip()
                        ]
                        logger.debug(
                            f"Parsed {len(analysis['prerequisites'])} prerequisites"
                        )
                    elif "Dependencies:" in section:
                        deps = section.split("Dependencies:")[1].strip().split("\n")
                        analysis["dependencies"] = [
                            d.strip("- ") for d in deps if d.strip()
                        ]
                        logger.debug(
                            f"Parsed {len(analysis['dependencies'])} dependencies"
                        )
                except Exception as e:
                    logger.error(f"Error parsing section: {str(e)}", exc_info=True)

            return analysis

    def _validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the output of the agent"""
        required_fields = [
            "topics",
            "key_concepts",
            "complexity",
            "suggested_structure",
        ]

        logger.debug(f"Validating output fields: {', '.join(required_fields)}")

        # Check if all required fields are present
        for field in required_fields:
            if field not in output:
                logger.error(f"Missing required field: {field}")
                return False

            # Check if fields have valid values
            if field in ["topics", "key_concepts"] and not isinstance(
                output[field], list
            ):
                logger.error(f"Field {field} must be a list, got {type(output[field])}")
                return False
            elif field in ["complexity", "suggested_structure"] and not isinstance(
                output[field], str
            ):
                logger.error(
                    f"Field {field} must be a string, got {type(output[field])}"
                )
                return False

            # Check if lists have content
            if field in ["topics", "key_concepts"] and not output[field]:
                logger.warning(f"Field {field} is empty")

        logger.debug("Output validation successful")
        return True
