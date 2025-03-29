import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from ..schemas.content_schemas import (ContentFormat, ContentGenerationRequest,
                                       ContentGenerationResult, ContentStyle,
                                       ContentType, ContentValidationResult,
                                       ExampleContent, ExerciseContent,
                                       GeneratedContent, InteractiveContent,
                                       VisualContent)
from ..schemas.message_schemas import AgentResponse, AgentTask
from ..schemas.module_schemas import Module, ModuleContent, ModuleType
from .base_agent import BaseAgent


class ContentGeneratorAgent(BaseAgent):
    """Agent responsible for generating learning content."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_templates = self._load_content_templates()

    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        Process a content generation task.
        Args:
            task: The task containing content generation request
        Returns:
            AgentResponse: The generated content
        """
        try:
            # Extract generation request from task
            request = task.task_data.get("request")
            if not request:
                raise ValueError("Missing content generation request")

            # Generate content
            content = await self._generate_content(request)

            # Validate content
            validation_result = self._validate_content(content)

            # Create generation result
            result = ContentGenerationResult(
                request_id=request.module_id,
                status="completed",
                content=content,
                completed_at=datetime.utcnow(),
            )

            return AgentResponse(
                task_id=task.message_id, result=result.dict(), error=None
            )

        except Exception as e:
            self.logger.error(f"Content generation failed: {str(e)}")
            return AgentResponse(task_id=task.message_id, result=None, error=str(e))

    def _load_content_templates(self) -> Dict[str, str]:
        """Load content generation templates."""
        return {
            "example": """
                Concept: {concept}
                Explanation: {explanation}

                Steps:
                {steps}

                Tips:
                {tips}

                Common Mistakes to Avoid:
                {common_mistakes}
            """,
            "exercise": """
                Question: {question}

                Options:
                {options}

                Correct Answer: {correct_answer}
                Explanation: {explanation}

                Difficulty Level: {difficulty_level}

                Hints:
                {hints}
            """,
            "visual": """
                Title: {title}
                Description: {description}

                Type: {type}
                Data: {data}

                Style: {style}
            """,
        }

    async def _generate_content(
        self, request: ContentGenerationRequest
    ) -> GeneratedContent:
        """
        Generate content based on request.
        Args:
            request: Content generation request
        Returns:
            GeneratedContent: Generated content
        """
        if request.content_type == ContentType.EXAMPLE:
            return await self._generate_example(request)
        elif request.content_type == ContentType.EXERCISE:
            return await self._generate_exercise(request)
        elif request.content_type == ContentType.VISUAL:
            return await self._generate_visual(request)
        elif request.content_type == ContentType.INTERACTIVE:
            return await self._generate_interactive(request)
        else:
            return await self._generate_text(request)

    async def _generate_example(
        self, request: ContentGenerationRequest
    ) -> ExampleContent:
        """Generate example content."""
        # Extract key concepts and create example structure
        concept = request.topic
        explanation = self._generate_explanation(concept, request.difficulty_level)
        steps = self._generate_steps(concept)
        tips = self._generate_tips(concept)
        common_mistakes = self._generate_common_mistakes(concept)

        return ExampleContent(
            type=ContentType.EXAMPLE,
            format=request.format,
            style=request.style,
            content=self.content_templates["example"].format(
                concept=concept,
                explanation=explanation,
                steps="\n".join(f"- {step}" for step in steps),
                tips="\n".join(f"- {tip}" for tip in tips),
                common_mistakes="\n".join(
                    f"- {mistake}" for mistake in common_mistakes
                ),
            ),
            concept=concept,
            explanation=explanation,
            steps=steps,
            tips=tips,
            common_mistakes=common_mistakes,
        )

    async def _generate_exercise(
        self, request: ContentGenerationRequest
    ) -> ExerciseContent:
        """Generate exercise content."""
        # Create exercise based on topic and difficulty
        question = self._generate_question(request.topic, request.difficulty_level)
        options = self._generate_options(question)
        correct_answer = self._determine_correct_answer(question, options)
        explanation = self._generate_explanation(
            correct_answer, request.difficulty_level
        )
        hints = self._generate_hints(question, correct_answer)

        return ExerciseContent(
            type=ContentType.EXERCISE,
            format=request.format,
            style=request.style,
            content=self.content_templates["exercise"].format(
                question=question,
                options="\n".join(f"- {option}" for option in options),
                correct_answer=correct_answer,
                explanation=explanation,
                difficulty_level=request.difficulty_level,
                hints="\n".join(f"- {hint}" for hint in hints),
            ),
            question=question,
            options=options,
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty_level=request.difficulty_level,
            hints=hints,
        )

    async def _generate_visual(
        self, request: ContentGenerationRequest
    ) -> VisualContent:
        """Generate visual content."""
        # Determine appropriate visual type and data
        visual_type = self._determine_visual_type(request.topic)
        data = self._generate_visual_data(request.topic, visual_type)
        style = self._generate_visual_style(request.style)

        return VisualContent(
            type=ContentType.VISUAL,
            format=request.format,
            style=request.style,
            content=self.content_templates["visual"].format(
                title=request.topic,
                description=self._generate_visual_description(request.topic),
                type=visual_type,
                data=json.dumps(data),
                style=json.dumps(style),
            ),
            title=request.topic,
            description=self._generate_visual_description(request.topic),
            type=visual_type,
            data=data,
            style=style,
        )

    async def _generate_interactive(
        self, request: ContentGenerationRequest
    ) -> InteractiveContent:
        """Generate interactive content."""
        # Determine appropriate interactive component
        component_type = self._determine_interactive_type(request.topic)
        configuration = self._generate_interactive_config(request.topic, component_type)
        dependencies = self._determine_dependencies(component_type)
        events = self._generate_events(component_type)

        return InteractiveContent(
            type=ContentType.INTERACTIVE,
            format=request.format,
            style=request.style,
            content=json.dumps(
                {
                    "component_type": component_type,
                    "configuration": configuration,
                    "dependencies": dependencies,
                    "events": events,
                }
            ),
            component_type=component_type,
            configuration=configuration,
            dependencies=dependencies,
            events=events,
        )

    async def _generate_text(
        self, request: ContentGenerationRequest
    ) -> GeneratedContent:
        """Generate text content."""
        content = self._generate_text_content(
            request.topic, request.difficulty_level, request.style
        )

        return GeneratedContent(
            type=ContentType.TEXT,
            format=request.format,
            style=request.style,
            content=content,
        )

    def _generate_explanation(self, concept: str, difficulty_level: str) -> str:
        """Generate explanation for a concept."""
        # Simple explanation generation based on difficulty
        if difficulty_level == "beginner":
            return f"{concept} is a fundamental concept that..."
        elif difficulty_level == "intermediate":
            return f"{concept} involves several key aspects..."
        else:
            return f"{concept} is a complex topic that requires understanding of..."

    def _generate_steps(self, concept: str) -> List[str]:
        """Generate steps for understanding a concept."""
        return [
            f"First, understand the basic definition of {concept}",
            f"Next, identify the key components of {concept}",
            f"Then, explore how {concept} is applied in practice",
            f"Finally, analyze real-world examples of {concept}",
        ]

    def _generate_tips(self, concept: str) -> List[str]:
        """Generate tips for understanding a concept."""
        return [
            f"Break down {concept} into smaller parts",
            f"Create visual representations of {concept}",
            f"Practice applying {concept} in different contexts",
            f"Review examples of {concept} regularly",
        ]

    def _generate_common_mistakes(self, concept: str) -> List[str]:
        """Generate common mistakes related to a concept."""
        return [
            f"Confusing {concept} with similar concepts",
            f"Overcomplicating the understanding of {concept}",
            f"Not practicing enough with {concept}",
            f"Missing key aspects of {concept}",
        ]

    def _generate_question(self, topic: str, difficulty_level: str) -> str:
        """Generate a question about a topic."""
        question_templates = {
            "beginner": f"What is the basic definition of {topic}?",
            "intermediate": f"How would you explain the relationship between {topic} and its components?",
            "advanced": f"Analyze the impact of {topic} in different contexts.",
        }
        return question_templates.get(
            difficulty_level, f"Explain the concept of {topic}."
        )

    def _generate_options(self, question: str) -> List[str]:
        """Generate answer options for a question."""
        # Simple option generation
        return [
            "Option A: First possible answer",
            "Option B: Second possible answer",
            "Option C: Third possible answer",
            "Option D: Fourth possible answer",
        ]

    def _determine_correct_answer(self, question: str, options: List[str]) -> str:
        """Determine the correct answer from options."""
        # Simple correct answer determination
        return options[0]  # For demonstration, always first option

    def _generate_hints(self, question: str, correct_answer: str) -> List[str]:
        """Generate hints for answering a question."""
        return [
            "Consider the key concepts involved",
            "Think about real-world applications",
            "Review related examples",
            "Break down the question into parts",
        ]

    def _determine_visual_type(self, topic: str) -> str:
        """Determine appropriate visual type for a topic."""
        if "process" in topic.lower() or "flow" in topic.lower():
            return "flowchart"
        elif "compare" in topic.lower() or "versus" in topic.lower():
            return "comparison"
        elif "structure" in topic.lower() or "hierarchy" in topic.lower():
            return "hierarchy"
        else:
            return "concept_map"

    def _generate_visual_data(self, topic: str, visual_type: str) -> Dict[str, Any]:
        """Generate data for visual content."""
        # Simple data generation based on visual type
        return {
            "nodes": [
                {"id": "1", "label": topic},
                {"id": "2", "label": "Related Concept 1"},
                {"id": "3", "label": "Related Concept 2"},
            ],
            "edges": [{"from": "1", "to": "2"}, {"from": "1", "to": "3"}],
        }

    def _generate_visual_style(self, style: ContentStyle) -> Dict[str, Any]:
        """Generate style for visual content."""
        return {
            "colors": ["#4CAF50", "#2196F3", "#FFC107"],
            "font": "Arial",
            "size": "medium",
        }

    def _generate_visual_description(self, topic: str) -> str:
        """Generate description for visual content."""
        return f"This visual representation helps understand the concept of {topic}."

    def _determine_interactive_type(self, topic: str) -> str:
        """Determine appropriate interactive component type."""
        if "quiz" in topic.lower():
            return "quiz"
        elif "simulation" in topic.lower():
            return "simulation"
        elif "practice" in topic.lower():
            return "practice"
        else:
            return "exploration"

    def _generate_interactive_config(
        self, topic: str, component_type: str
    ) -> Dict[str, Any]:
        """Generate configuration for interactive component."""
        return {
            "title": topic,
            "type": component_type,
            "settings": {"difficulty": "medium", "time_limit": 300, "attempts": 3},
        }

    def _determine_dependencies(self, component_type: str) -> List[str]:
        """Determine dependencies for interactive component."""
        return ["jquery", "bootstrap", "interactive-js"]

    def _generate_events(self, component_type: str) -> List[str]:
        """Generate events for interactive component."""
        return ["onStart", "onProgress", "onComplete", "onError"]

    def _generate_text_content(
        self, topic: str, difficulty_level: str, style: ContentStyle
    ) -> str:
        """Generate text content based on parameters."""
        # Generate content based on style and difficulty
        if style == ContentStyle.FORMAL:
            return f"This formal explanation of {topic} covers..."
        elif style == ContentStyle.CASUAL:
            return f"Let's explore {topic} in a casual way..."
        elif style == ContentStyle.TECHNICAL:
            return f"The technical aspects of {topic} include..."
        else:
            return f"Hey there! Let's chat about {topic}..."

    def _validate_content(self, content: GeneratedContent) -> ContentValidationResult:
        """
        Validate generated content.
        Args:
            content: Content to validate
        Returns:
            ContentValidationResult: Validation results
        """
        issues = []
        suggestions = []

        # Basic content validation
        if not content.content:
            issues.append("Empty content")

        # Format-specific validation
        if content.format == ContentFormat.MARKDOWN:
            if not self._validate_markdown(content.content):
                issues.append("Invalid markdown format")

        # Style validation
        if not self._validate_style(content.content, content.style):
            issues.append("Style inconsistency")

        # Generate readability score
        readability_score = self._calculate_readability(content.content)

        # Generate complexity score
        complexity_score = self._calculate_complexity(content.content)

        return ContentValidationResult(
            content_id=content.content_id,
            is_valid=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            readability_score=readability_score,
            complexity_score=complexity_score,
        )

    def _validate_markdown(self, content: str) -> bool:
        """Validate markdown content."""
        # Basic markdown validation
        return bool(re.match(r"^#", content))  # Check for at least one heading

    def _validate_style(self, content: str, style: ContentStyle) -> bool:
        """Validate content style."""
        # Style-specific validation
        if style == ContentStyle.FORMAL:
            return not any(
                word in content.lower() for word in ["hey", "cool", "awesome"]
            )
        elif style == ContentStyle.CASUAL:
            return any(word in content.lower() for word in ["hey", "cool", "awesome"])
        return True

    def _calculate_readability(self, content: str) -> float:
        """Calculate content readability score."""
        # Simple readability calculation
        words = content.split()
        sentences = content.split(".")
        if not sentences:
            return 0.0

        avg_words_per_sentence = len(words) / len(sentences)
        return max(0.0, min(1.0, 1.0 - (avg_words_per_sentence / 20)))

    def _calculate_complexity(self, content: str) -> float:
        """Calculate content complexity score."""
        # Simple complexity calculation
        words = content.split()
        long_words = sum(1 for word in words if len(word) > 6)
        return min(1.0, long_words / len(words))
