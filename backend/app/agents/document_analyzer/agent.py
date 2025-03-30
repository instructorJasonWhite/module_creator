"""Document analyzer agent for analyzing documents."""

import json
import logging
import os
from typing import Any, Dict

import openai
from app.core.base_agent import AgentConfig, BaseAgent

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DocumentAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing educational documents."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the agent with configuration."""
        try:
            msg = "Initializing DocumentAnalyzerAgent with config: {}"
            logger.debug(msg.format(config))
            agent_config = AgentConfig(**config)
            super().__init__(agent_config)
            # Create outlines directory if it doesn't exist
            base = os.path.dirname
            base_dir = base(base(base(__file__)))
            outlines_dir = os.path.join(
                base(base_dir),
                "outputs",
                "outlines"
            )
            os.makedirs(outlines_dir, exist_ok=True)
            logger.info("Successfully initialized DocumentAnalyzerAgent")
        except Exception as e:
            msg = "Failed to initialize DocumentAnalyzerAgent: {}"
            logger.error(msg.format(str(e)), exc_info=True)
            raise

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input document and generate analysis."""
        try:
            logger.debug("=== Starting Document Analysis ===")
            logger.debug("Input data keys: {}".format(input_data.keys()))

            # Validate input data
            if not input_data.get("document_text"):
                raise ValueError("No document text provided")

            # Get model settings
            model_settings = await self._get_model_settings()
            logger.debug("Using model settings: {}".format(model_settings))

            # Format prompt
            prompt = self._format_prompt(input_data)
            logger.debug("Formatted prompt length: {}".format(len(prompt)))

            # Execute LLM
            response = await self._execute_llm(prompt, model_settings)
            logger.debug("Raw LLM response: {}...".format(response[:200]))

            # Parse response
            result = self._parse_response(response)
            logger.debug("Structured result: {}".format(result))

            # Validate output
            self._validate_output(result)
            logger.debug("Output validation successful")

            # Save outline if original filename is provided
            outline_file = None
            if input_data.get("original_filename"):
                try:
                    # Create outlines directory if it doesn't exist
                    base = os.path.dirname
                    base_dir = base(base(base(__file__)))
                    outlines_dir = os.path.join(
                        base(base_dir),
                        "outputs",
                        "outlines"
                    )
                    os.makedirs(outlines_dir, exist_ok=True)
                    msg = "Created/verified outlines directory: {}"
                    logger.debug(msg.format(outlines_dir))

                    # Generate outline filename
                    base_name = os.path.splitext(
                        input_data["original_filename"]
                    )[0]
                    outline_filename = "{}_outline.txt".format(base_name)
                    outline_path = os.path.join(
                        outlines_dir, outline_filename
                    )

                    # Format and save outline
                    outline_content = self._format_outline(result)
                    msg = "Formatted outline length: {}"
                    logger.debug(msg.format(len(outline_content)))

                    with open(outline_path, "w", encoding="utf-8") as f:
                        f.write(outline_content)

                    outline_file = outline_filename
                    logger.info("Saved outline to: {}".format(outline_path))
                except Exception as e:
                    msg = "Error saving outline: {}"
                    logger.error(msg.format(str(e)), exc_info=True)
            else:
                msg = "No original filename provided, skipping outline save"
                logger.warning(msg)

            # Return response
            response_data = {
                "status": "success",
                "analysis": result,
                "outline_file": outline_file,
            }
            logger.debug("Returning response data: {}".format(response_data))
            return response_data

        except Exception as e:
            msg = "Error in document analysis: {}"
            logger.error(msg.format(str(e)), exc_info=True)
            raise

    def _format_prompt(self, input_data: Dict[str, Any]) -> str:
        """Format the prompt template with input data."""
        try:
            document_text = input_data.get("document_text", "")
            context = input_data.get("agent_context", "")

            # Truncate document text if too long (approximately 4000 tokens)
            max_doc_length = 8000  # Conservative limit for input text
            if len(document_text) > max_doc_length:
                msg = (
                    "Document text too long ({} chars), "
                    "truncating to {} chars"
                )
                logger.warning(
                    msg.format(len(document_text), max_doc_length)
                )
                document_text = document_text[:max_doc_length] + "..."

            prompt = self.config.prompt_template.format(
                document_text=document_text,
                context=context
            )
            logger.debug("Formatted prompt length: {}".format(len(prompt)))
            return prompt
        except Exception as e:
            msg = "Error formatting prompt: {}"
            logger.error(msg.format(str(e)), exc_info=True)
            raise

    async def _execute_llm(self, prompt: str, model_settings: Dict[str, Any]) -> str:
        """Execute the language model with the given prompt."""
        try:
            # Set up OpenAI client
            msg = "Setting up OpenAI client with model: {}"
            logger.debug(msg.format(model_settings.get("model_name")))
            client = openai.OpenAI(api_key=model_settings.get("api_key"))

            # Get max tokens from model settings
            max_tokens = model_settings.get("max_tokens", 2000)  # Default to 2000
            msg = "Using max tokens from model settings: {}"
            logger.debug(msg.format(max_tokens))

            # Prepare messages for the chat completion
            system_msg = (
                "You are an expert educational content analyzer. "
                "Your task is to analyze documents and provide "
                "structured analysis in JSON format."
            )
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ]
            logger.debug("Prepared messages for OpenAI API call")

            # Call OpenAI API synchronously
            logger.debug("Making OpenAI API call...")
            model_name = model_settings.get("model_name", "gpt-3.5-turbo")
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=model_settings.get("temperature", 0.7),
                max_tokens=max_tokens,
            )
            logger.debug("Received response from OpenAI API")

            # Extract the response content
            content = response.choices[0].message.content
            logger.debug("Raw LLM response: {}".format(content[:200]))
            return content

        except Exception as e:
            msg = "Error executing LLM: {}"
            logger.error(msg.format(str(e)), exc_info=True)
            logger.error("Model settings used: {}".format(model_settings))
            raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured format."""
        try:
            # Try to parse the response as JSON
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON-like structure
                msg = "Response is not valid JSON, attempting to extract"
                logger.warning(msg)
                # Look for JSON-like content between curly braces
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                    result = json.loads(json_str)
                else:
                    msg = "Could not find valid JSON structure in response"
                    raise ValueError(msg)

            # Validate and structure the result
            structured_result = {
                "topics": result.get("topics", []),
                "subtopics": result.get("subtopics", {}),
                "key_concepts": result.get("key_concepts", []),
                "complexity": result.get("complexity", "Unknown"),
                "suggested_structure": result.get(
                    "suggested_structure", "No structure suggested"
                ),
                "prerequisites": result.get("prerequisites", []),
                "dependencies": result.get("dependencies", []),
            }

            logger.debug("Structured result: {}".format(structured_result))
            return structured_result

        except Exception as e:
            msg = "Error parsing response: {}"
            logger.error(msg.format(str(e)), exc_info=True)
            raise

    def _validate_output(self, output: Dict[str, Any]) -> None:
        """Validate the output structure."""
        required_fields = [
            "topics",
            "subtopics",
            "key_concepts",
            "complexity",
            "suggested_structure",
            "prerequisites",
            "dependencies",
        ]
        for field in required_fields:
            if field not in output:
                msg = "Missing required field: {}"
                raise ValueError(msg.format(field))
        logger.debug("Output validation successful")

    def _format_outline(self, result: Dict[str, Any]) -> str:
        """Format the analysis result into a readable outline."""
        logger.debug("Starting outline formatting")
        outline = []

        # Add document analysis section
        outline.append("=== Document Analysis ===")
        outline.append("")

        # Add main topics
        outline.append("Main Topics:")
        for topic in result.get("topics", []):
            outline.append("- {}".format(topic))
            # Add subtopics if they exist
            if topic in result.get("subtopics", {}):
                for subtopic in result["subtopics"][topic]:
                    outline.append("  * {}".format(subtopic))

        # Add key concepts
        outline.append("\nKey Concepts:")
        for concept in result.get("key_concepts", []):
            outline.append("- {}".format(concept))

        # Add complexity level
        outline.append(
            "\nComplexity Level: {}".format(result.get("complexity", "Unknown"))
        )

        # Add suggested structure
        outline.append(
            "\nSuggested Structure:\n{}".format(
                result.get("suggested_structure", "No structure suggested")
            )
        )

        # Add prerequisites if any
        if result.get("prerequisites"):
            outline.append("\nPrerequisites:")
            for prereq in result["prerequisites"]:
                outline.append("- {}".format(prereq))

        # Add dependencies if any
        if result.get("dependencies"):
            outline.append("\nDependencies:")
            for dep in result["dependencies"]:
                outline.append("- {}".format(dep))

        # Add detailed outline section
        outline.append("\n=== Detailed Outline ===")
        outline.append("")

        # Create a hierarchical outline
        for topic in result.get("topics", []):
            outline.append("1. {}".format(topic))
            if topic in result.get("subtopics", {}):
                for i, subtopic in enumerate(result["subtopics"][topic], 1):
                    outline.append("   {}. {}".format(i, subtopic))
                    # Add related key concepts for this subtopic
                    related = [
                        c
                        for c in result.get("key_concepts", [])
                        if any(kw in c.lower() for kw in subtopic.lower().split())
                    ]
                    if related:
                        outline.append("      Key Concepts:")
                        for concept in related:
                            outline.append("      - {}".format(concept))

        formatted_outline = "\n".join(outline)
        msg = "Formatted outline length: {} chars"
        logger.debug(msg.format(len(formatted_outline)))
        return formatted_outline
