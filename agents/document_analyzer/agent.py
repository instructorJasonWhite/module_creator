import json
from typing import Any, Dict

from backend.core.base_agent import BaseAgent


class DocumentAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing educational documents"""

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
            # Format the prompt with input data
            messages = self._format_prompt(input_data)

            # Execute the LLM
            response = await self._execute_llm(messages)

            # Parse the response
            analysis = self._parse_response(response)

            # Validate the output
            if not self._validate_output(analysis):
                raise ValueError("Invalid analysis output")

            # Send results to module planner
            await self.send_message(
                "module_planner", {"type": "document_analysis", "data": analysis}
            )

            return {
                "status": "success",
                "agent": self.config.name,
                "analysis": analysis,
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
            # This is a simple example - you might want to make this more robust
            sections = response.split("\n\n")
            analysis = {
                "topics": [],
                "subtopics": {},
                "key_concepts": [],
                "complexity": "",
                "suggested_structure": [],
            }

            current_section = None
            for section in sections:
                if section.startswith("Topics:"):
                    current_section = "topics"
                    analysis["topics"] = [
                        t.strip()
                        for t in section.replace("Topics:", "").split("\n")
                        if t.strip()
                    ]
                elif section.startswith("Key Concepts:"):
                    current_section = "key_concepts"
                    analysis["key_concepts"] = [
                        c.strip()
                        for c in section.replace("Key Concepts:", "").split("\n")
                        if c.strip()
                    ]
                elif section.startswith("Complexity:"):
                    analysis["complexity"] = section.replace("Complexity:", "").strip()
                elif section.startswith("Suggested Structure:"):
                    analysis["suggested_structure"] = [
                        s.strip()
                        for s in section.replace("Suggested Structure:", "").split("\n")
                        if s.strip()
                    ]

            return analysis

    def _validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the analysis output"""
        required_fields = [
            "topics",
            "key_concepts",
            "complexity",
            "suggested_structure",
        ]
        return all(field in output for field in required_fields)
