import json
from typing import Any, Dict

from backend.core.base_agent import BaseAgent


class ContentGeneratorAgent(BaseAgent):
    """Agent responsible for generating educational content"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate educational content for a module section

        Args:
            input_data: Dictionary containing:
                - topic: Topic to generate content for
                - learning_objectives: Specific objectives for this section
                - target_audience: Description of target audience
                - difficulty_level: Target difficulty level
                - module_plan: Optional plan from module planner

        Returns:
            Dictionary containing:
                - content: Generated content sections
                - examples: List of examples
                - visual_suggestions: Suggested visual elements
                - interactive_elements: Suggested interactive components
        """
        try:
            # Format the prompt with input data
            messages = self._format_prompt(input_data)

            # Execute the LLM
            response = await self._execute_llm(messages)

            # Parse the response
            content = self._parse_response(response)

            # Validate the output
            if not self._validate_output(content):
                raise ValueError("Invalid content output")

            # Send results to quiz generator
            await self.send_message(
                "quiz_generator", {"type": "content", "data": content}
            )

            return {
                "status": "success",
                "agent": self.config.name,
                "content": content,
            }

        except Exception as e:
            return await self._handle_error(e)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data"""
        try:
            # Attempt to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If not JSON, try to extract structured data from text
            sections = response.split("\n\n")
            content = {
                "content": [],
                "examples": [],
                "visual_suggestions": [],
                "interactive_elements": [],
            }

            current_section = None
            for section in sections:
                if section.startswith("Content:"):
                    current_section = "content"
                    content["content"] = [
                        c.strip()
                        for c in section.replace("Content:", "").split("\n")
                        if c.strip()
                    ]
                elif section.startswith("Examples:"):
                    current_section = "examples"
                    content["examples"] = [
                        e.strip()
                        for e in section.replace("Examples:", "").split("\n")
                        if e.strip()
                    ]
                elif section.startswith("Visual Suggestions:"):
                    current_section = "visual_suggestions"
                    content["visual_suggestions"] = [
                        v.strip()
                        for v in section.replace("Visual Suggestions:", "").split("\n")
                        if v.strip()
                    ]
                elif section.startswith("Interactive Elements:"):
                    current_section = "interactive_elements"
                    content["interactive_elements"] = [
                        i.strip()
                        for i in section.replace("Interactive Elements:", "").split("\n")
                        if i.strip()
                    ]

            return content

    def _validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the content output"""
        required_fields = [
            "content",
            "examples",
            "visual_suggestions",
            "interactive_elements",
        ]
        return all(field in output for field in required_fields) 