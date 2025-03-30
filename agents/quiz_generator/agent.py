import json
from typing import Any, Dict

from backend.core.base_agent import BaseAgent


class QuizGeneratorAgent(BaseAgent):
    """Agent responsible for generating assessments and quizzes"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate assessments and quizzes for a module section

        Args:
            input_data: Dictionary containing:
                - content: The content to generate questions for
                - learning_objectives: Specific objectives to test
                - difficulty_level: Target difficulty level
                - question_types: List of desired question types
                - content_data: Optional content from content generator

        Returns:
            Dictionary containing:
                - questions: List of generated questions
                - answers: Dictionary mapping questions to answers
                - explanations: Dictionary mapping questions to explanations
                - difficulty_ratings: Dictionary mapping questions to difficulty ratings
        """
        try:
            # Format the prompt with input data
            messages = self._format_prompt(input_data)

            # Execute the LLM
            response = await self._execute_llm(messages)

            # Parse the response
            quiz = self._parse_response(response)

            # Validate the output
            if not self._validate_output(quiz):
                raise ValueError("Invalid quiz output")

            # Send results to quality assurance
            await self.send_message(
                "quality_assurance", {"type": "quiz", "data": quiz}
            )

            return {
                "status": "success",
                "agent": self.config.name,
                "quiz": quiz,
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
            quiz = {
                "questions": [],
                "answers": {},
                "explanations": {},
                "difficulty_ratings": {},
            }

            current_question = None
            for section in sections:
                if section.startswith("Question:"):
                    current_question = section.replace("Question:", "").strip()
                    quiz["questions"].append(current_question)
                elif section.startswith("Answer:") and current_question:
                    quiz["answers"][current_question] = section.replace("Answer:", "").strip()
                elif section.startswith("Explanation:") and current_question:
                    quiz["explanations"][current_question] = section.replace("Explanation:", "").strip()
                elif section.startswith("Difficulty:") and current_question:
                    difficulty = section.replace("Difficulty:", "").strip()
                    try:
                        quiz["difficulty_ratings"][current_question] = float(difficulty.split()[0])
                    except (ValueError, IndexError):
                        quiz["difficulty_ratings"][current_question] = 0.0

            return quiz

    def _validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the quiz output"""
        required_fields = [
            "questions",
            "answers",
            "explanations",
            "difficulty_ratings",
        ]
        return all(field in output for field in required_fields) 