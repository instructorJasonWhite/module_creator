import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from ..schemas.document_schemas import ContentComplexity, DocumentAnalysis
from ..schemas.message_schemas import AgentResponse, AgentTask
from ..schemas.module_schemas import (LearningObjective, Module, ModuleContent,
                                      ModulePlan, ModulePlanningResult,
                                      ModulePlanningStatus, ModuleType)
from .base_agent import BaseAgent


class ModulePlannerAgent(BaseAgent):
    """Agent responsible for planning learning modules from document analysis."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bloom_levels = [
            "Remember",
            "Understand",
            "Apply",
            "Analyze",
            "Evaluate",
            "Create",
        ]

    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        Process a module planning task.
        Args:
            task: The task containing document analysis
        Returns:
            AgentResponse: The module planning results
        """
        try:
            # Extract document analysis from task
            document_analysis = task.task_data.get("document_analysis")
            if not document_analysis:
                raise ValueError("Missing document analysis data")

            # Create module plan
            plan = await self._create_module_plan(document_analysis)

            # Create planning result
            result = ModulePlanningResult(
                plan_id=plan.plan_id,
                status=ModulePlanningStatus.COMPLETED,
                plan=plan,
                completed_at=datetime.utcnow(),
            )

            return AgentResponse(
                task_id=task.message_id, result=result.dict(), error=None
            )

        except Exception as e:
            self.logger.error(f"Module planning failed: {str(e)}")
            return AgentResponse(task_id=task.message_id, result=None, error=str(e))

    async def _create_module_plan(self, analysis: DocumentAnalysis) -> ModulePlan:
        """
        Create a module plan from document analysis.
        Args:
            analysis: Document analysis results
        Returns:
            ModulePlan: Complete module plan
        """
        # Create modules from sections
        modules = await self._create_modules(analysis.sections)

        # Optimize learning path
        learning_path = self._optimize_learning_path(modules)

        # Calculate total duration
        total_duration = sum(module.total_duration for module in modules)

        return ModulePlan(
            document_id=analysis.document_id,
            title=f"Learning Modules: {analysis.title}",
            description=f"Structured learning path for {analysis.title}",
            target_audience=analysis.target_audience,
            modules=modules,
            total_duration=total_duration,
            difficulty_level=analysis.overall_complexity.value,
            prerequisites=analysis.prerequisites,
            learning_path=learning_path,
            metadata={
                "original_document": analysis.title,
                "author": analysis.author,
                "creation_date": analysis.creation_date,
                "last_modified": analysis.last_modified,
            },
        )

    async def _create_modules(self, sections: List[DocumentSection]) -> List[Module]:
        """
        Create learning modules from document sections.
        Args:
            sections: Document sections
        Returns:
            List[Module]: List of learning modules
        """
        modules = []
        current_module = None

        for section in sections:
            # Create new module for top-level sections
            if section.level <= 2:
                if current_module:
                    modules.append(current_module)

                current_module = Module(
                    title=section.title,
                    description=section.content[:200]
                    + "...",  # First 200 chars as description
                    level=section.level,
                    difficulty_level=section.complexity.value,
                    learning_objectives=self._create_learning_objectives(section),
                )

            # Add content to current module
            if current_module:
                content = self._create_module_content(section)
                current_module.contents.append(content)

        # Add the last module
        if current_module:
            modules.append(current_module)

        return modules

    def _create_learning_objectives(
        self, section: DocumentSection
    ) -> List[LearningObjective]:
        """
        Create learning objectives for a section.
        Args:
            section: Document section
        Returns:
            List[LearningObjective]: List of learning objectives
        """
        objectives = []

        # Create objectives based on section content
        for keyword in section.keywords:
            objective = LearningObjective(
                description=f"Understand and apply the concept of {keyword}",
                bloom_level=self._determine_bloom_level(section.complexity),
                assessment_criteria=[
                    f"Can explain the concept of {keyword}",
                    f"Can apply {keyword} in relevant contexts",
                    f"Can analyze relationships involving {keyword}",
                ],
            )
            objectives.append(objective)

        return objectives

    def _create_module_content(self, section: DocumentSection) -> ModuleContent:
        """
        Create module content from a section.
        Args:
            section: Document section
        Returns:
            ModuleContent: Module content
        """
        # Determine content type based on section level and content
        content_type = self._determine_content_type(section)

        return ModuleContent(
            type=content_type,
            title=section.title,
            content=section.content,
            estimated_duration=self._estimate_duration(section),
            difficulty_level=section.complexity.value,
            interactive_elements=self._suggest_interactive_elements(content_type),
            visual_aids=self._suggest_visual_aids(section),
            examples=self._extract_examples(section),
            exercises=self._generate_exercises(section),
        )

    def _determine_content_type(self, section: DocumentSection) -> ModuleType:
        """Determine the type of content based on section characteristics."""
        if section.level == 1:
            return ModuleType.INTRODUCTION
        elif "example" in section.title.lower():
            return ModuleType.EXAMPLE
        elif "exercise" in section.title.lower() or "practice" in section.title.lower():
            return ModuleType.EXERCISE
        elif "quiz" in section.title.lower() or "test" in section.title.lower():
            return ModuleType.QUIZ
        elif section.level == max(section.level, 6):  # Lowest level section
            return ModuleType.SUMMARY
        else:
            return ModuleType.CONCEPT

    def _determine_bloom_level(self, complexity: ContentComplexity) -> str:
        """Determine Bloom's taxonomy level based on content complexity."""
        if complexity == ContentComplexity.BEGINNER:
            return self.bloom_levels[0]  # Remember
        elif complexity == ContentComplexity.INTERMEDIATE:
            return self.bloom_levels[2]  # Apply
        else:
            return self.bloom_levels[4]  # Evaluate

    def _estimate_duration(self, section: DocumentSection) -> int:
        """Estimate duration for a section in minutes."""
        # Rough estimation based on word count
        word_count = len(section.content.split())
        return max(5, min(60, word_count // 100))  # 5-60 minutes

    def _suggest_interactive_elements(self, content_type: ModuleType) -> List[str]:
        """Suggest interactive elements based on content type."""
        suggestions = {
            ModuleType.INTRODUCTION: ["Overview", "Key Points", "Navigation Guide"],
            ModuleType.CONCEPT: [
                "Concept Map",
                "Interactive Diagram",
                "Definition Cards",
            ],
            ModuleType.EXAMPLE: [
                "Step-by-Step Guide",
                "Interactive Example",
                "Practice Problem",
            ],
            ModuleType.EXERCISE: [
                "Interactive Quiz",
                "Practice Exercise",
                "Progress Tracker",
            ],
            ModuleType.QUIZ: ["Multiple Choice", "True/False", "Matching Exercise"],
            ModuleType.SUMMARY: ["Key Takeaways", "Review Questions", "Next Steps"],
        }
        return suggestions.get(content_type, [])

    def _suggest_visual_aids(self, section: DocumentSection) -> List[str]:
        """Suggest visual aids based on section content."""
        visual_aids = []

        # Look for concepts that might benefit from visual representation
        for keyword in section.keywords:
            if len(keyword.split()) > 1:  # Multi-word concepts
                visual_aids.append(f"Diagram for {keyword}")
            if any(char.isdigit() for char in keyword):  # Numerical concepts
                visual_aids.append(f"Chart for {keyword}")

        return visual_aids

    def _extract_examples(self, section: DocumentSection) -> List[str]:
        """Extract examples from section content."""
        examples = []
        example_keywords = ["example", "for instance", "such as", "like", "including"]

        sentences = section.content.split(". ")
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in example_keywords):
                examples.append(sentence.strip())

        return examples

    def _generate_exercises(self, section: DocumentSection) -> List[str]:
        """Generate exercises based on section content."""
        exercises = []

        # Create exercises for each key concept
        for keyword in section.keywords:
            exercises.extend(
                [
                    f"Explain the concept of {keyword} in your own words",
                    f"Provide a real-world example of {keyword}",
                    f"Compare and contrast {keyword} with related concepts",
                    f"Apply {keyword} to solve a practical problem",
                ]
            )

        return exercises

    def _optimize_learning_path(self, modules: List[Module]) -> List[UUID]:
        """
        Optimize the learning path based on prerequisites and complexity.
        Args:
            modules: List of modules
        Returns:
            List[UUID]: Optimized sequence of module IDs
        """
        # Create dependency graph
        graph = defaultdict(list)
        for module in modules:
            for prereq_id in module.prerequisites:
                graph[prereq_id].append(module.module_id)

        # Topological sort for prerequisite ordering
        visited = set()
        path = []

        def visit(module_id: UUID):
            if module_id in visited:
                return
            visited.add(module_id)
            for next_id in graph[module_id]:
                visit(next_id)
            path.append(module_id)

        # Start with modules that have no prerequisites
        for module in modules:
            if not module.prerequisites:
                visit(module.module_id)

        # Add any remaining modules
        for module in modules:
            if module.module_id not in visited:
                visit(module.module_id)

        return path
