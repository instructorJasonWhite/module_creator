"""Document analyzer agent for analyzing documents."""

import json
import logging
import os
from typing import Any, Dict

import openai
from app.core.base_agent import AgentConfig, BaseAgent
from app.services.user_preferences import UserPreferencesService

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
            outlines_dir = os.path.join(base(base_dir), "outputs", "outlines")
            os.makedirs(outlines_dir, exist_ok=True)
            logger.info("Successfully initialized DocumentAnalyzerAgent")
        except Exception as e:
            msg = "Failed to initialize DocumentAnalyzerAgent: {}"
            logger.error(msg.format(str(e)), exc_info=True)
            raise

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a document and analyze its content."""
        try:
            # Log the input data
            msg = "=== Starting Document Analysis ==="
            logger.debug(msg)
            msg = "Input data keys: {}"
            logger.debug(msg.format(input_data.keys()))

            # Validate input data
            self._validate_input(input_data)
            logger.debug("Input validation successful")

            # Get user preferences if available
            user_preferences = None
            if input_data.get("agent_context"):
                user_preferences = self._extract_user_preferences(
                    input_data["agent_context"]
                )

            # Get model settings
            model_settings = await self._get_model_settings()
            logger.debug("Using model settings: {}".format(model_settings))

            # Format prompt with user preferences if available
            prompt = self._format_prompt(input_data, user_preferences)
            logger.debug("Formatted prompt length: {}".format(len(prompt)))

            # Execute LLM
            llm_response = await self._execute_llm(prompt, model_settings)

            # Check if the response is already processed
            if isinstance(llm_response, dict) and "raw_response" in llm_response:
                # Handle the raw string response
                response = llm_response["raw_response"]
                logger.debug(
                    "Using raw response from LLM: {}...".format(response[:200])
                )
                # Parse the raw response
                result = self._parse_response(response)
            elif isinstance(llm_response, dict):
                # The response is already in a structured format
                logger.debug("LLM returned structured response")
                # Format the response to match expected structure
                result = {
                    "topics": llm_response.get("topics", []),
                    "subtopics": llm_response.get("subtopics", {}),
                    "key_concepts": llm_response.get("key_concepts", []),
                    "complexity": llm_response.get("complexity", "Unknown"),
                    "suggested_structure": llm_response.get(
                        "suggested_structure", "No structure suggested"
                    ),
                    "prerequisites": llm_response.get("prerequisites", []),
                    "dependencies": llm_response.get("dependencies", []),
                }
            else:
                # Handle unexpected response type
                logger.warning(f"Unexpected response type: {type(llm_response)}")
                response = str(llm_response)
                result = self._parse_response(response)

            logger.debug("Structured result: {}".format(result))

            # Validate output
            self._validate_output(result)
            logger.debug("Output validation successful")

            # Adjust number of modules based on user preferences if available
            if user_preferences and user_preferences.number_of_modules:
                result["suggested_structure"] = self._adjust_module_count(
                    result["suggested_structure"], user_preferences.number_of_modules
                )

            # Save outline if original filename is provided
            outline_file = None
            if input_data.get("original_filename"):
                try:
                    # Create outlines directory if it doesn't exist
                    base = os.path.dirname
                    base_dir = base(base(base(__file__)))
                    outlines_dir = os.path.join(base(base_dir), "outputs", "outlines")
                    os.makedirs(outlines_dir, exist_ok=True)
                    msg = "Created/verified outlines directory: {}"
                    logger.debug(msg.format(outlines_dir))

                    # Generate outline filename
                    base_name = os.path.splitext(input_data["original_filename"])[0]
                    outline_filename = f"{base_name}_outline.txt"
                    outline_path = os.path.join(outlines_dir, outline_filename)

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

    def _format_prompt(
        self, input_data: Dict[str, Any], user_preferences: Any = None
    ) -> str:
        """Format the prompt template with input data and user preferences."""
        try:
            document_text = input_data.get("document_text", "")
            context = input_data.get("agent_context", "")

            # Add user preferences to context if available
            if user_preferences:
                context += f"\nUser Preferences:\n"
                context += (
                    f"- Number of modules: {user_preferences.number_of_modules}\n"
                )
                if user_preferences.theme_prompt:
                    context += f"- Theme: {user_preferences.theme_prompt}\n"
                if user_preferences.module_preferences:
                    context += "- Module preferences:\n"
                    for pref in user_preferences.module_preferences:
                        context += f"  * Module {pref.module_index}: {pref.format}\n"

            # Truncate document text if too long (approximately 4000 tokens)
            max_doc_length = 8000  # Conservative limit for input text
            if len(document_text) > max_doc_length:
                msg = "Document text too long ({} chars), " "truncating to {} chars"
                logger.warning(msg.format(len(document_text), max_doc_length))
                document_text = document_text[:max_doc_length] + "..."

            prompt = self.config.prompt_template.format(
                document_text=document_text, context=context
            )
            logger.debug("Formatted prompt length: {}".format(len(prompt)))
            return prompt
        except Exception as e:
            msg = "Error formatting prompt: {}"
            logger.error(msg.format(str(e)), exc_info=True)
            raise

    def _adjust_module_count(self, structure: str, target_count: int) -> str:
        """Adjust the suggested structure to match the target module count."""
        try:
            # Split the structure into modules
            modules = [m.strip() for m in structure.split("->")]

            # If we have more modules than needed, combine some
            if len(modules) > target_count:
                # Calculate how many modules to combine
                combine_count = len(modules) - target_count
                # Combine modules from the end
                for i in range(combine_count):
                    modules[-2] = f"{modules[-2]} & {modules[-1]}"
                    modules.pop()

            # Join modules back together
            return " -> ".join(modules)
        except Exception as e:
            msg = "Error adjusting module count: {}"
            logger.error(msg.format(str(e)), exc_info=True)
            return structure

    async def _execute_llm(self, prompt: str, model_settings: dict) -> dict:
        """Execute the LLM call to analyze the document."""
        logger.debug("=== Starting LLM execution ===")
        logger.debug(f"Model settings received: {model_settings}")

        try:
            # Set up OpenAI client
            logger.debug("Setting up OpenAI client configuration")

            import inspect

            import openai

            # Log available parameters for OpenAI client constructor
            logger.debug(f"OpenAI version: {openai.__version__}")
            logger.debug(
                f"OpenAI client params: {inspect.signature(openai.OpenAI.__init__)}"
            )

            config = {
                "api_key": model_settings.get("api_key"),
                "base_url": "https://api.openai.com/v1",
                "timeout": 60,
                "max_retries": 3,
            }

            logger.debug(
                f"OpenAI client config (without API key): {dict(config, **{'api_key': '[REDACTED]'})}"
            )

            # Initialize the client
            logger.debug("Initializing OpenAI client")
            client = openai.OpenAI(api_key=model_settings.get("api_key"))
            logger.debug("OpenAI client initialized successfully")

            # Get max tokens
            max_tokens = model_settings.get("max_tokens", 2000)
            logger.debug(f"Using max_tokens: {max_tokens}")

            # Prepare messages for OpenAI API
            logger.debug("Preparing messages for OpenAI API")
            messages = [
                {
                    "role": "system",
                    "content": "You are an educational content analyzer.",
                },
                {"role": "user", "content": prompt},
            ]
            logger.debug(
                f"Prepared {len(messages)} messages, total characters: {sum(len(m['content']) for m in messages)}"
            )

            # Make API call
            logger.debug(
                f"Making API call to model: {model_settings.get('model_name', 'gpt-3.5-turbo')}"
            )
            completion = client.chat.completions.create(
                model=model_settings.get("model_name", "gpt-3.5-turbo"),
                messages=messages,
                max_tokens=max_tokens,
                temperature=model_settings.get("temperature", 0.7),
            )
            logger.debug("API call completed successfully")

            # Process response
            logger.debug("Processing response")
            response = completion.choices[0].message.content
            logger.debug(f"Response length: {len(response)} characters")

            try:
                # Try to parse the response as JSON
                logger.debug("Attempting to parse response as JSON")
                import json

                parsed_response = json.loads(response)
                logger.debug("Successfully parsed response as JSON")
                return parsed_response
            except json.JSONDecodeError:
                # If it's not valid JSON, return the raw response
                logger.debug("Response is not valid JSON, returning raw response")
                return {"raw_response": response}

        except Exception as e:
            logger.error(f"Error executing LLM: {str(e)}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
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

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate the input data for the agent."""
        if not input_data.get("document_text"):
            raise ValueError("No document text provided")
        logger.debug("Input validation successful")

    def _extract_user_preferences(self, agent_context: Dict[str, Any]) -> Any:
        """Extract user preferences from agent context."""
        try:
            if not agent_context:
                return None

            logger.debug(f"Extracting user preferences from context: {agent_context}")

            # Create a simple preferences object with expected properties
            class Preferences:
                def __init__(self):
                    self.number_of_modules = None
                    self.theme_prompt = None
                    self.module_preferences = []

            preferences = Preferences()

            # Check if context contains user preferences
            if isinstance(agent_context, dict):
                preferences_data = agent_context.get("user_preferences", {})
                if preferences_data:
                    preferences.number_of_modules = preferences_data.get(
                        "number_of_modules"
                    )
                    preferences.theme_prompt = preferences_data.get("theme")
                    module_prefs = preferences_data.get("module_preferences", [])

                    # Process module preferences
                    class ModulePreference:
                        def __init__(self, module_index, format_type):
                            self.module_index = module_index
                            self.format = format_type

                    for pref in module_prefs:
                        if (
                            isinstance(pref, dict)
                            and "module_index" in pref
                            and "format" in pref
                        ):
                            preferences.module_preferences.append(
                                ModulePreference(pref["module_index"], pref["format"])
                            )

            logger.debug(
                f"Extracted preferences: number_of_modules={preferences.number_of_modules}, theme={preferences.theme_prompt}, module_prefs_count={len(preferences.module_preferences)}"
            )
            return preferences
        except Exception as e:
            logger.error(f"Error extracting user preferences: {str(e)}")
            return None
