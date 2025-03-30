import json
from typing import Any, Dict

from backend.core.base_agent import BaseAgent


class QualityAssuranceAgent(BaseAgent):
    """Agent responsible for reviewing and validating content and quizzes"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and validate content or quizzes

        Args:
            input_data: Dictionary containing:
                - type: Type of content to review ("content" or "quiz")
                - data: The content or quiz data to review
                - learning_objectives: Learning objectives to validate against
                - target_audience: Target audience for content appropriateness
                - difficulty_level: Expected difficulty level

        Returns:
            Dictionary containing:
                - status: Review status ("approved", "needs_revision", "rejected")
                - feedback: List of feedback items
                - suggestions: List of improvement suggestions
                - quality_score: Overall quality score (0-100)
        """
        try:
            # Format the prompt with input data
            messages = self._format_prompt(input_data)

            # Execute the LLM
            response = await self._execute_llm(messages)

            # Parse the response
            review = self._parse_response(response)

            # Validate the output
            if not self._validate_output(review):
                raise ValueError("Invalid review output")

            return {
                "status": "success",
                "agent": self.config.name,
                "review": review,
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
            review = {
                "status": "needs_revision",
                "feedback": [],
                "suggestions": [],
                "quality_score": 0,
            }

            for section in sections:
                if section.startswith("Status:"):
                    review["status"] = section.replace("Status:", "").strip().lower()
                elif section.startswith("Feedback:"):
                    feedback = section.replace("Feedback:", "").strip()
                    review["feedback"] = [f.strip() for f in feedback.split("\n") if f.strip()]
                elif section.startswith("Suggestions:"):
                    suggestions = section.replace("Suggestions:", "").strip()
                    review["suggestions"] = [s.strip() for s in suggestions.split("\n") if s.strip()]
                elif section.startswith("Quality Score:"):
                    try:
                        review["quality_score"] = float(section.replace("Quality Score:", "").strip())
                    except (ValueError, IndexError):
                        review["quality_score"] = 0.0

            return review

    def _validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the review output"""
        required_fields = [
            "status",
            "feedback",
            "suggestions",
            "quality_score",
        ]
        return all(field in output for field in required_fields) 