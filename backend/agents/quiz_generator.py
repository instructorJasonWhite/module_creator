import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from ..schemas.message_schemas import AgentResponse, AgentTask
from ..schemas.quiz_schemas import (AnswerOption, BloomTaxonomyLevel,
                                    DifficultyLevel, Question, QuestionType,
                                    Quiz, QuizGenerationRequest,
                                    QuizGenerationResult, QuizValidationResult)
from .base_agent import BaseAgent


class QuizGeneratorAgent(BaseAgent):
    """Agent responsible for generating educational quizzes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question_templates = self._load_question_templates()
        self.bloom_verbs = self._load_bloom_verbs()

    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        Process a quiz generation task.
        Args:
            task: The task containing quiz generation request
        Returns:
            AgentResponse: The generated quiz
        """
        try:
            # Extract quiz generation request from task
            request = task.task_data.get("request")
            if not request:
                raise ValueError("Missing quiz generation request")

            # Generate quiz
            quiz = await self._generate_quiz(request)

            # Validate quiz
            validation_result = self._validate_quiz(quiz)

            # Create generation result
            result = QuizGenerationResult(
                request_id=request.module_id,
                status="completed",
                quiz=quiz,
                completed_at=datetime.utcnow(),
            )

            return AgentResponse(
                task_id=task.message_id, result=result.dict(), error=None
            )

        except Exception as e:
            self.logger.error(f"Quiz generation failed: {str(e)}")
            return AgentResponse(task_id=task.message_id, result=None, error=str(e))

    def _load_question_templates(self) -> Dict[str, str]:
        """Load question generation templates."""
        return {
            "multiple_choice": """
                Question: {question}

                Options:
                {options}

                Correct Answer: {correct_answer}
                Explanation: {explanation}

                Difficulty: {difficulty}
                Bloom Level: {bloom_level}

                Hints:
                {hints}
            """,
            "true_false": """
                Statement: {statement}

                Answer: {answer}
                Explanation: {explanation}

                Difficulty: {difficulty}
                Bloom Level: {bloom_level}

                Hints:
                {hints}
            """,
            "short_answer": """
                Question: {question}

                Correct Answer: {correct_answer}
                Explanation: {explanation}

                Difficulty: {difficulty}
                Bloom Level: {bloom_level}

                Hints:
                {hints}
            """,
            "matching": """
                Instructions: {instructions}

                Items:
                {items}

                Correct Matches:
                {matches}

                Explanation: {explanation}

                Difficulty: {difficulty}
                Bloom Level: {bloom_level}

                Hints:
                {hints}
            """,
            "fill_in_blank": """
                Statement: {statement}

                Correct Answer: {correct_answer}
                Explanation: {explanation}

                Difficulty: {difficulty}
                Bloom Level: {bloom_level}

                Hints:
                {hints}
            """,
        }

    def _load_bloom_verbs(self) -> Dict[BloomTaxonomyLevel, List[str]]:
        """Load Bloom's Taxonomy verbs."""
        return {
            BloomTaxonomyLevel.REMEMBER: [
                "define",
                "describe",
                "identify",
                "list",
                "name",
                "recall",
                "recognize",
                "state",
            ],
            BloomTaxonomyLevel.UNDERSTAND: [
                "explain",
                "interpret",
                "outline",
                "discuss",
                "distinguish",
                "predict",
                "restate",
                "translate",
            ],
            BloomTaxonomyLevel.APPLY: [
                "solve",
                "illustrate",
                "calculate",
                "use",
                "interpret",
                "relate",
                "manipulate",
                "apply",
            ],
            BloomTaxonomyLevel.ANALYZE: [
                "analyze",
                "organize",
                "deduce",
                "choose",
                "compare",
                "contrast",
                "examine",
                "test",
            ],
            BloomTaxonomyLevel.EVALUATE: [
                "evaluate",
                "assess",
                "determine",
                "measure",
                "select",
                "defend",
                "judge",
                "value",
            ],
            BloomTaxonomyLevel.CREATE: [
                "create",
                "design",
                "hypothesize",
                "support",
                "schematize",
                "write",
                "report",
                "justify",
            ],
        }

    async def _generate_quiz(self, request: QuizGenerationRequest) -> Quiz:
        """
        Generate a quiz based on the request.
        Args:
            request: Quiz generation request
        Returns:
            Quiz: Generated quiz
        """
        # Extract key concepts from content
        concepts = self._extract_key_concepts(request.content)

        # Generate questions
        questions = []
        for _ in range(request.question_count):
            question_type = self._select_question_type(request.question_types)
            bloom_level = self._select_bloom_level(request.bloom_levels)
            concept = self._select_concept(concepts)

            question = await self._generate_question(
                concept=concept,
                question_type=question_type,
                difficulty=request.difficulty,
                bloom_level=bloom_level,
            )
            questions.append(question)

        # Calculate total points and passing score
        total_points = len(questions) * 10
        passing_score = int(total_points * 0.7)  # 70% passing threshold

        return Quiz(
            title=f"Quiz for Module {request.module_id}",
            description=f"Assessment covering key concepts from the module",
            module_id=request.module_id,
            questions=questions,
            difficulty=request.difficulty,
            total_points=total_points,
            passing_score=passing_score,
            time_limit=len(questions) * 2,  # 2 minutes per question
            metadata={
                "concepts_covered": concepts,
                "generation_timestamp": datetime.utcnow().isoformat(),
            },
        )

    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts from content."""
        # Simple concept extraction
        sentences = content.split(".")
        concepts = []
        for sentence in sentences:
            if len(sentence.split()) >= 3:  # Avoid very short sentences
                concepts.append(sentence.strip())
        return concepts[:10]  # Limit to top 10 concepts

    def _select_question_type(self, question_types: List[QuestionType]) -> QuestionType:
        """Select a question type."""
        if not question_types:
            return QuestionType.MULTIPLE_CHOICE
        return question_types[0]  # For now, just use the first type

    def _select_bloom_level(
        self, bloom_levels: List[BloomTaxonomyLevel]
    ) -> BloomTaxonomyLevel:
        """Select a Bloom's Taxonomy level."""
        if not bloom_levels:
            return BloomTaxonomyLevel.UNDERSTAND
        return bloom_levels[0]  # For now, just use the first level

    def _select_concept(self, concepts: List[str]) -> str:
        """Select a concept for question generation."""
        if not concepts:
            return "General knowledge"
        return concepts[0]  # For now, just use the first concept

    async def _generate_question(
        self,
        concept: str,
        question_type: QuestionType,
        difficulty: DifficultyLevel,
        bloom_level: BloomTaxonomyLevel,
    ) -> Question:
        """Generate a question based on parameters."""
        if question_type == QuestionType.MULTIPLE_CHOICE:
            return await self._generate_multiple_choice(
                concept=concept, difficulty=difficulty, bloom_level=bloom_level
            )
        elif question_type == QuestionType.TRUE_FALSE:
            return await self._generate_true_false(
                concept=concept, difficulty=difficulty, bloom_level=bloom_level
            )
        elif question_type == QuestionType.SHORT_ANSWER:
            return await self._generate_short_answer(
                concept=concept, difficulty=difficulty, bloom_level=bloom_level
            )
        elif question_type == QuestionType.MATCHING:
            return await self._generate_matching(
                concept=concept, difficulty=difficulty, bloom_level=bloom_level
            )
        else:
            return await self._generate_fill_in_blank(
                concept=concept, difficulty=difficulty, bloom_level=bloom_level
            )

    async def _generate_multiple_choice(
        self, concept: str, difficulty: DifficultyLevel, bloom_level: BloomTaxonomyLevel
    ) -> Question:
        """Generate a multiple choice question."""
        # Generate question text
        verb = self._select_bloom_verb(bloom_level)
        question_text = f"{verb} the following about {concept}?"

        # Generate options
        options = self._generate_answer_options(concept, difficulty)

        # Select correct answer
        correct_option = next(opt for opt in options if opt.is_correct)

        # Generate explanation
        explanation = self._generate_explanation(concept, correct_option.text)

        # Generate hints
        hints = self._generate_hints(concept, correct_option.text)

        return Question(
            type=QuestionType.MULTIPLE_CHOICE,
            text=question_text,
            difficulty=difficulty,
            bloom_level=bloom_level,
            options=options,
            correct_answer=correct_option.text,
            explanation=explanation,
            hints=hints,
            tags=[concept, difficulty.value, bloom_level.value],
        )

    async def _generate_true_false(
        self, concept: str, difficulty: DifficultyLevel, bloom_level: BloomTaxonomyLevel
    ) -> Question:
        """Generate a true/false question."""
        # Generate statement
        verb = self._select_bloom_verb(bloom_level)
        statement = f"{verb} the following statement about {concept}."

        # Generate true/false options
        options = [
            AnswerOption(
                text="True", is_correct=True, explanation="This statement is correct."
            ),
            AnswerOption(
                text="False",
                is_correct=False,
                explanation="This statement is incorrect.",
            ),
        ]

        # Select correct answer
        correct_option = next(opt for opt in options if opt.is_correct)

        # Generate explanation
        explanation = self._generate_explanation(concept, correct_option.text)

        # Generate hints
        hints = self._generate_hints(concept, correct_option.text)

        return Question(
            type=QuestionType.TRUE_FALSE,
            text=statement,
            difficulty=difficulty,
            bloom_level=bloom_level,
            options=options,
            correct_answer=correct_option.text,
            explanation=explanation,
            hints=hints,
            tags=[concept, difficulty.value, bloom_level.value],
        )

    async def _generate_short_answer(
        self, concept: str, difficulty: DifficultyLevel, bloom_level: BloomTaxonomyLevel
    ) -> Question:
        """Generate a short answer question."""
        # Generate question text
        verb = self._select_bloom_verb(bloom_level)
        question_text = f"{verb} the following about {concept}?"

        # Generate correct answer
        correct_answer = self._generate_short_answer_response(concept)

        # Generate explanation
        explanation = self._generate_explanation(concept, correct_answer)

        # Generate hints
        hints = self._generate_hints(concept, correct_answer)

        return Question(
            type=QuestionType.SHORT_ANSWER,
            text=question_text,
            difficulty=difficulty,
            bloom_level=bloom_level,
            options=[],  # No options for short answer
            correct_answer=correct_answer,
            explanation=explanation,
            hints=hints,
            tags=[concept, difficulty.value, bloom_level.value],
        )

    async def _generate_matching(
        self, concept: str, difficulty: DifficultyLevel, bloom_level: BloomTaxonomyLevel
    ) -> Question:
        """Generate a matching question."""
        # Generate items to match
        items = self._generate_matching_items(concept)

        # Generate instructions
        instructions = f"Match the following items related to {concept}."

        # Generate correct matches
        matches = self._generate_correct_matches(items)

        # Generate explanation
        explanation = self._generate_explanation(concept, "matching exercise")

        # Generate hints
        hints = self._generate_hints(concept, "matching exercise")

        return Question(
            type=QuestionType.MATCHING,
            text=instructions,
            difficulty=difficulty,
            bloom_level=bloom_level,
            options=[],  # No options for matching
            correct_answer=json.dumps(matches),
            explanation=explanation,
            hints=hints,
            tags=[concept, difficulty.value, bloom_level.value],
        )

    async def _generate_fill_in_blank(
        self, concept: str, difficulty: DifficultyLevel, bloom_level: BloomTaxonomyLevel
    ) -> Question:
        """Generate a fill-in-the-blank question."""
        # Generate statement with blank
        verb = self._select_bloom_verb(bloom_level)
        statement = f"{verb} the following about {concept}: [BLANK]"

        # Generate correct answer
        correct_answer = self._generate_fill_in_blank_answer(concept)

        # Generate explanation
        explanation = self._generate_explanation(concept, correct_answer)

        # Generate hints
        hints = self._generate_hints(concept, correct_answer)

        return Question(
            type=QuestionType.FILL_IN_BLANK,
            text=statement,
            difficulty=difficulty,
            bloom_level=bloom_level,
            options=[],  # No options for fill-in-blank
            correct_answer=correct_answer,
            explanation=explanation,
            hints=hints,
            tags=[concept, difficulty.value, bloom_level.value],
        )

    def _select_bloom_verb(self, bloom_level: BloomTaxonomyLevel) -> str:
        """Select a verb for the given Bloom's Taxonomy level."""
        verbs = self.bloom_verbs.get(bloom_level, [])
        if not verbs:
            return "Consider"
        return verbs[0]  # For now, just use the first verb

    def _generate_answer_options(
        self, concept: str, difficulty: DifficultyLevel
    ) -> List[AnswerOption]:
        """Generate answer options for multiple choice questions."""
        # Simple option generation
        return [
            AnswerOption(
                text=f"Option A about {concept}",
                is_correct=True,
                explanation="This is the correct answer.",
            ),
            AnswerOption(
                text=f"Option B about {concept}",
                is_correct=False,
                explanation="This is incorrect.",
            ),
            AnswerOption(
                text=f"Option C about {concept}",
                is_correct=False,
                explanation="This is incorrect.",
            ),
            AnswerOption(
                text=f"Option D about {concept}",
                is_correct=False,
                explanation="This is incorrect.",
            ),
        ]

    def _generate_explanation(self, concept: str, answer: str) -> str:
        """Generate explanation for an answer."""
        return f"This answer is correct because it accurately describes {concept}."

    def _generate_hints(self, concept: str, answer: str) -> List[str]:
        """Generate hints for answering a question."""
        return [
            f"Consider the key aspects of {concept}",
            "Think about the relationships between concepts",
            "Review any examples provided",
            "Consider the context carefully",
        ]

    def _generate_short_answer_response(self, concept: str) -> str:
        """Generate a short answer response."""
        return f"A comprehensive answer about {concept}"

    def _generate_matching_items(self, concept: str) -> List[str]:
        """Generate items for matching questions."""
        return [
            f"Item 1 related to {concept}",
            f"Item 2 related to {concept}",
            f"Item 3 related to {concept}",
            f"Item 4 related to {concept}",
        ]

    def _generate_correct_matches(self, items: List[str]) -> Dict[str, str]:
        """Generate correct matches for matching questions."""
        return {
            items[0]: "Match 1",
            items[1]: "Match 2",
            items[2]: "Match 3",
            items[3]: "Match 4",
        }

    def _generate_fill_in_blank_answer(self, concept: str) -> str:
        """Generate a fill-in-the-blank answer."""
        return f"The correct answer about {concept}"

    def _validate_quiz(self, quiz: Quiz) -> QuizValidationResult:
        """
        Validate generated quiz.
        Args:
            quiz: Quiz to validate
        Returns:
            QuizValidationResult: Validation results
        """
        issues = []
        suggestions = []

        # Check question count
        if len(quiz.questions) < 5:
            issues.append("Quiz has too few questions")
            suggestions.append("Add more questions to ensure comprehensive coverage")

        # Check difficulty distribution
        difficulty_distribution = defaultdict(int)
        for question in quiz.questions:
            difficulty_distribution[question.difficulty] += 1

        # Check Bloom's Taxonomy distribution
        bloom_distribution = defaultdict(int)
        for question in quiz.questions:
            bloom_distribution[question.bloom_level] += 1

        # Validate each question
        for question in quiz.questions:
            if not question.text:
                issues.append(f"Question {question.question_id} has no text")
            if not question.correct_answer:
                issues.append(f"Question {question.question_id} has no correct answer")
            if not question.explanation:
                issues.append(f"Question {question.question_id} has no explanation")

        return QuizValidationResult(
            quiz_id=quiz.quiz_id,
            is_valid=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            difficulty_distribution=difficulty_distribution,
            bloom_distribution=bloom_distribution,
            metadata={"validation_timestamp": datetime.utcnow().isoformat()},
        )
