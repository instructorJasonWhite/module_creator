import json
from typing import Any, Dict

from backend.core.base_agent import BaseAgent


class ModulePlannerAgent(BaseAgent):
    """Agent responsible for planning the structure of learning modules"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan the structure of a learning module

        Args:
            input_data: Dictionary containing:
                - topics: List of topics to cover
                - learning_objectives: List of learning objectives
                - target_audience: Description of target audience
                - duration: Target duration in hours
                - document_analysis: Optional analysis from document analyzer

        Returns:
            Dictionary containing:
                - module_structure: List of module sections
                - prerequisites: List of prerequisites
                - learning_path: Suggested learning sequence
                - estimated_duration: Estimated duration per section
        """
        try:
            # Format the prompt with input data
            messages = self._format_prompt(input_data)

            # Execute the LLM
            response = await self._execute_llm(messages)

            # Parse the response
            plan = self._parse_response(response)

            # Validate the output
            if not self._validate_output(plan):
                raise ValueError("Invalid module plan output")

            # Send results to content generator
            await self.send_message(
                "content_generator", {"type": "module_plan", "data": plan}
            )

            return {
                "status": "success",
                "agent": self.config.name,
                "plan": plan,
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
            plan = {
                "module_structure": [],
                "prerequisites": [],
                "learning_path": [],
                "estimated_duration": {},
            }

            current_section = None
            for section in sections:
                if section.startswith("Module Structure:"):
                    current_section = "module_structure"
                    plan["module_structure"] = [
                        s.strip()
                        for s in section.replace("Module Structure:", "").split("\n")
                        if s.strip()
                    ]
                elif section.startswith("Prerequisites:"):
                    current_section = "prerequisites"
                    plan["prerequisites"] = [
                        p.strip()
                        for p in section.replace("Prerequisites:", "").split("\n")
                        if p.strip()
                    ]
                elif section.startswith("Learning Path:"):
                    current_section = "learning_path"
                    plan["learning_path"] = [
                        p.strip()
                        for p in section.replace("Learning Path:", "").split("\n")
                        if p.strip()
                    ]
                elif section.startswith("Estimated Duration:"):
                    current_section = "estimated_duration"
                    duration_text = section.replace("Estimated Duration:", "").strip()
                    # Parse duration text into a dictionary
                    plan["estimated_duration"] = self._parse_duration(duration_text)

            return plan

    def _parse_duration(self, duration_text: str) -> Dict[str, float]:
        """Parse duration text into a dictionary of section durations"""
        durations = {}
        for line in duration_text.split("\n"):
            if ":" in line:
                section, duration = line.split(":", 1)
                try:
                    durations[section.strip()] = float(duration.strip().split()[0])
                except (ValueError, IndexError):
                    continue
        return durations

    def _validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the module plan output"""
        required_fields = [
            "module_structure",
            "prerequisites",
            "learning_path",
            "estimated_duration",
        ]
        return all(field in output for field in required_fields)
