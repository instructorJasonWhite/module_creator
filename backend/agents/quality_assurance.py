import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from ..schemas.message_schemas import AgentResponse, AgentTask
from ..schemas.quality_schemas import (AccessibilityCheck, AccuracyCheck,
                                       CompletenessCheck, EngagementMetrics,
                                       QualityAssessment, QualityCheckRequest,
                                       QualityCheckResult, QualityImprovement,
                                       QualityLevel, QualityMetric,
                                       QualityScore)
from .base_agent import BaseAgent


class QualityAssuranceAgent(BaseAgent):
    """Agent responsible for quality assurance of generated content."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quality_thresholds = self._load_quality_thresholds()
        self.required_elements = self._load_required_elements()

    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        Process a quality assurance task.
        Args:
            task: The task containing quality check request
        Returns:
            AgentResponse: The quality assessment results
        """
        try:
            # Extract quality check request from task
            request = task.task_data.get("request")
            if not request:
                raise ValueError("Missing quality check request")

            # Perform quality assessment
            assessment = await self._perform_quality_assessment(request)

            # Generate improvement suggestions
            improvements = self._generate_improvements(assessment)

            # Create quality check result
            result = QualityCheckResult(
                request_id=request.content_id,
                status="completed",
                assessment=assessment,
                completed_at=datetime.utcnow(),
            )

            return AgentResponse(
                task_id=task.message_id, result=result.dict(), error=None
            )

        except Exception as e:
            self.logger.error(f"Quality assessment failed: {str(e)}")
            return AgentResponse(task_id=task.message_id, result=None, error=str(e))

    def _load_quality_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load quality thresholds for different metrics."""
        return {
            "readability": {
                "excellent": 0.8,
                "good": 0.6,
                "satisfactory": 0.4,
                "needs_improvement": 0.2,
            },
            "complexity": {
                "excellent": 0.2,
                "good": 0.4,
                "satisfactory": 0.6,
                "needs_improvement": 0.8,
            },
            "accuracy": {
                "excellent": 0.9,
                "good": 0.7,
                "satisfactory": 0.5,
                "needs_improvement": 0.3,
            },
            "completeness": {
                "excellent": 0.9,
                "good": 0.7,
                "satisfactory": 0.5,
                "needs_improvement": 0.3,
            },
            "engagement": {
                "excellent": 0.8,
                "good": 0.6,
                "satisfactory": 0.4,
                "needs_improvement": 0.2,
            },
            "accessibility": {
                "excellent": 0.9,
                "good": 0.7,
                "satisfactory": 0.5,
                "needs_improvement": 0.3,
            },
        }

    def _load_required_elements(self) -> Dict[str, List[str]]:
        """Load required elements for different content types."""
        return {
            "text": ["title", "introduction", "main_content", "conclusion"],
            "example": ["concept", "explanation", "steps", "tips"],
            "exercise": ["question", "options", "correct_answer", "explanation"],
            "visual": ["title", "description", "data", "style"],
            "interactive": [
                "component_type",
                "configuration",
                "dependencies",
                "events",
            ],
        }

    async def _perform_quality_assessment(
        self, request: QualityCheckRequest
    ) -> QualityAssessment:
        """
        Perform comprehensive quality assessment.
        Args:
            request: Quality check request
        Returns:
            QualityAssessment: Assessment results
        """
        # Calculate individual metrics
        readability_score = self._assess_readability(request.content)
        complexity_score = self._assess_complexity(request.content)
        accuracy_score = self._assess_accuracy(request.content)
        completeness_score = self._assess_completeness(
            request.content, request.content_type
        )
        engagement_score = self._assess_engagement(request.content)
        accessibility_score = self._assess_accessibility(request.content)

        # Create quality scores
        metrics = [
            QualityScore(
                metric=QualityMetric.READABILITY,
                score=readability_score,
                level=self._determine_quality_level("readability", readability_score),
                details={
                    "words_per_sentence": self._calculate_words_per_sentence(
                        request.content
                    )
                },
                suggestions=self._generate_readability_suggestions(readability_score),
            ),
            QualityScore(
                metric=QualityMetric.COMPLEXITY,
                score=complexity_score,
                level=self._determine_quality_level("complexity", complexity_score),
                details={
                    "long_words_ratio": self._calculate_long_words_ratio(
                        request.content
                    )
                },
                suggestions=self._generate_complexity_suggestions(complexity_score),
            ),
            QualityScore(
                metric=QualityMetric.ACCURACY,
                score=accuracy_score,
                level=self._determine_quality_level("accuracy", accuracy_score),
                details={
                    "consistency_score": self._calculate_consistency_score(
                        request.content
                    )
                },
                suggestions=self._generate_accuracy_suggestions(accuracy_score),
            ),
            QualityScore(
                metric=QualityMetric.COMPLETENESS,
                score=completeness_score,
                level=self._determine_quality_level("completeness", completeness_score),
                details={
                    "missing_elements": self._identify_missing_elements(
                        request.content, request.content_type
                    )
                },
                suggestions=self._generate_completeness_suggestions(completeness_score),
            ),
            QualityScore(
                metric=QualityMetric.ENGAGEMENT,
                score=engagement_score,
                level=self._determine_quality_level("engagement", engagement_score),
                details={
                    "interactivity_score": self._calculate_interactivity_score(
                        request.content
                    )
                },
                suggestions=self._generate_engagement_suggestions(engagement_score),
            ),
            QualityScore(
                metric=QualityMetric.ACCESSIBILITY,
                score=accessibility_score,
                level=self._determine_quality_level(
                    "accessibility", accessibility_score
                ),
                details={
                    "wcag_compliance": self._check_wcag_compliance(request.content)
                },
                suggestions=self._generate_accessibility_suggestions(
                    accessibility_score
                ),
            ),
        ]

        # Calculate overall score and level
        overall_score = sum(metric.score for metric in metrics) / len(metrics)
        overall_level = self._determine_quality_level("overall", overall_score)

        # Collect issues and recommendations
        issues = self._collect_issues(metrics)
        recommendations = self._generate_recommendations(metrics)

        return QualityAssessment(
            content_id=request.content_id,
            overall_score=overall_score,
            overall_level=overall_level,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "content_type": request.content_type,
                "assessment_timestamp": datetime.utcnow().isoformat(),
            },
        )

    def _assess_readability(self, content: str) -> float:
        """Assess content readability."""
        words = content.split()
        sentences = content.split(".")
        if not sentences:
            return 0.0

        # Calculate average words per sentence
        avg_words_per_sentence = len(words) / len(sentences)

        # Calculate long words ratio
        long_words = sum(1 for word in words if len(word) > 6)
        long_words_ratio = long_words / len(words)

        # Calculate readability score (0-1)
        readability_score = 1.0 - (avg_words_per_sentence / 20) - (long_words_ratio / 2)
        return max(0.0, min(1.0, readability_score))

    def _assess_complexity(self, content: str) -> float:
        """Assess content complexity."""
        words = content.split()

        # Calculate long words ratio
        long_words = sum(1 for word in words if len(word) > 6)
        long_words_ratio = long_words / len(words)

        # Calculate technical terms ratio
        technical_terms = sum(1 for word in words if self._is_technical_term(word))
        technical_terms_ratio = technical_terms / len(words)

        # Calculate complexity score (0-1)
        complexity_score = (long_words_ratio + technical_terms_ratio) / 2
        return max(0.0, min(1.0, complexity_score))

    def _assess_accuracy(self, content: str) -> float:
        """Assess content accuracy."""
        # Check for factual consistency
        factual_consistency = self._check_factual_consistency(content)

        # Check for technical accuracy
        technical_accuracy = self._check_technical_accuracy(content)

        # Check for logical flow
        logical_flow = self._check_logical_flow(content)

        # Calculate accuracy score (0-1)
        accuracy_score = (factual_consistency + technical_accuracy + logical_flow) / 3
        return max(0.0, min(1.0, accuracy_score))

    def _assess_completeness(self, content: str, content_type: str) -> float:
        """Assess content completeness."""
        required_elements = self.required_elements.get(content_type, [])
        if not required_elements:
            return 1.0

        # Check for required elements
        present_elements = sum(
            1 for element in required_elements if self._has_element(content, element)
        )

        # Calculate completeness score (0-1)
        completeness_score = present_elements / len(required_elements)
        return max(0.0, min(1.0, completeness_score))

    def _assess_engagement(self, content: str) -> float:
        """Assess content engagement."""
        # Calculate interactivity score
        interactivity_score = self._calculate_interactivity_score(content)

        # Calculate visual appeal score
        visual_appeal = self._calculate_visual_appeal(content)

        # Calculate content flow score
        content_flow = self._calculate_content_flow(content)

        # Calculate user interest score
        user_interest = self._calculate_user_interest(content)

        # Calculate engagement score (0-1)
        engagement_score = (
            interactivity_score + visual_appeal + content_flow + user_interest
        ) / 4
        return max(0.0, min(1.0, engagement_score))

    def _assess_accessibility(self, content: str) -> float:
        """Assess content accessibility."""
        # Check WCAG compliance
        wcag_compliance = self._check_wcag_compliance(content)

        # Check for alternative text
        alt_text_score = self._check_alt_text(content)

        # Check for color contrast
        contrast_score = self._check_color_contrast(content)

        # Check for keyboard navigation
        keyboard_nav_score = self._check_keyboard_navigation(content)

        # Calculate accessibility score (0-1)
        accessibility_score = (
            wcag_compliance + alt_text_score + contrast_score + keyboard_nav_score
        ) / 4
        return max(0.0, min(1.0, accessibility_score))

    def _determine_quality_level(self, metric: str, score: float) -> QualityLevel:
        """Determine quality level based on score and thresholds."""
        thresholds = self.quality_thresholds.get(
            metric, self.quality_thresholds["overall"]
        )

        if score >= thresholds["excellent"]:
            return QualityLevel.EXCELLENT
        elif score >= thresholds["good"]:
            return QualityLevel.GOOD
        elif score >= thresholds["satisfactory"]:
            return QualityLevel.SATISFACTORY
        elif score >= thresholds["needs_improvement"]:
            return QualityLevel.NEEDS_IMPROVEMENT
        else:
            return QualityLevel.POOR

    def _calculate_words_per_sentence(self, content: str) -> float:
        """Calculate average words per sentence."""
        words = content.split()
        sentences = content.split(".")
        if not sentences:
            return 0.0
        return len(words) / len(sentences)

    def _calculate_long_words_ratio(self, content: str) -> float:
        """Calculate ratio of long words."""
        words = content.split()
        long_words = sum(1 for word in words if len(word) > 6)
        return long_words / len(words)

    def _is_technical_term(self, word: str) -> bool:
        """Check if a word is a technical term."""
        # Simple technical term detection
        technical_indicators = [
            "-",
            "_",
            "api",
            "sdk",
            "framework",
            "algorithm",
            "protocol",
        ]
        return any(indicator in word.lower() for indicator in technical_indicators)

    def _check_factual_consistency(self, content: str) -> float:
        """Check factual consistency of content."""
        # Simple consistency check
        return 0.8  # Placeholder

    def _check_technical_accuracy(self, content: str) -> float:
        """Check technical accuracy of content."""
        # Simple technical accuracy check
        return 0.8  # Placeholder

    def _check_logical_flow(self, content: str) -> float:
        """Check logical flow of content."""
        # Simple logical flow check
        return 0.8  # Placeholder

    def _has_element(self, content: str, element: str) -> bool:
        """Check if content has a specific element."""
        # Simple element detection
        return element.lower() in content.lower()

    def _calculate_interactivity_score(self, content: str) -> float:
        """Calculate interactivity score."""
        # Simple interactivity check
        return 0.7  # Placeholder

    def _calculate_visual_appeal(self, content: str) -> float:
        """Calculate visual appeal score."""
        # Simple visual appeal check
        return 0.7  # Placeholder

    def _calculate_content_flow(self, content: str) -> float:
        """Calculate content flow score."""
        # Simple content flow check
        return 0.7  # Placeholder

    def _calculate_user_interest(self, content: str) -> float:
        """Calculate user interest score."""
        # Simple user interest check
        return 0.7  # Placeholder

    def _check_wcag_compliance(self, content: str) -> float:
        """Check WCAG compliance."""
        # Simple WCAG compliance check
        return 0.8  # Placeholder

    def _check_alt_text(self, content: str) -> float:
        """Check for alternative text."""
        # Simple alt text check
        return 0.8  # Placeholder

    def _check_color_contrast(self, content: str) -> float:
        """Check color contrast."""
        # Simple color contrast check
        return 0.8  # Placeholder

    def _check_keyboard_navigation(self, content: str) -> float:
        """Check keyboard navigation."""
        # Simple keyboard navigation check
        return 0.8  # Placeholder

    def _collect_issues(self, metrics: List[QualityScore]) -> List[str]:
        """Collect issues from quality metrics."""
        issues = []
        for metric in metrics:
            if metric.level in [QualityLevel.NEEDS_IMPROVEMENT, QualityLevel.POOR]:
                issues.append(
                    f"{metric.metric.value}: {metric.score:.2f} - {metric.level.value}"
                )
        return issues

    def _generate_recommendations(self, metrics: List[QualityScore]) -> List[str]:
        """Generate recommendations based on quality metrics."""
        recommendations = []
        for metric in metrics:
            if metric.level in [QualityLevel.NEEDS_IMPROVEMENT, QualityLevel.POOR]:
                recommendations.extend(metric.suggestions)
        return recommendations

    def _generate_improvements(
        self, assessment: QualityAssessment
    ) -> List[QualityImprovement]:
        """Generate improvement suggestions."""
        improvements = []
        for metric in assessment.metrics:
            if metric.level in [QualityLevel.NEEDS_IMPROVEMENT, QualityLevel.POOR]:
                improvement = QualityImprovement(
                    content_id=assessment.content_id,
                    assessment_id=assessment.assessment_id,
                    improvements=[
                        {
                            "metric": metric.metric.value,
                            "current_score": metric.score,
                            "target_score": self.quality_thresholds[
                                metric.metric.value
                            ]["good"],
                            "suggestions": metric.suggestions,
                        }
                    ],
                    priority="high" if metric.level == QualityLevel.POOR else "medium",
                    estimated_effort="1-2 days",
                    impact="significant",
                )
                improvements.append(improvement)
        return improvements

    def _generate_readability_suggestions(self, score: float) -> List[str]:
        """Generate readability improvement suggestions."""
        suggestions = []
        if score < 0.6:
            suggestions.extend(
                [
                    "Break down long sentences into shorter ones",
                    "Use simpler vocabulary",
                    "Add more examples and explanations",
                    "Improve paragraph structure",
                ]
            )
        return suggestions

    def _generate_complexity_suggestions(self, score: float) -> List[str]:
        """Generate complexity improvement suggestions."""
        suggestions = []
        if score > 0.7:
            suggestions.extend(
                [
                    "Simplify technical terms",
                    "Add more explanations for complex concepts",
                    "Break down complex topics into smaller parts",
                    "Include more examples",
                ]
            )
        return suggestions

    def _generate_accuracy_suggestions(self, score: float) -> List[str]:
        """Generate accuracy improvement suggestions."""
        suggestions = []
        if score < 0.7:
            suggestions.extend(
                [
                    "Verify technical information",
                    "Add references and citations",
                    "Review for consistency",
                    "Include more detailed explanations",
                ]
            )
        return suggestions

    def _generate_completeness_suggestions(self, score: float) -> List[str]:
        """Generate completeness improvement suggestions."""
        suggestions = []
        if score < 0.7:
            suggestions.extend(
                [
                    "Add missing required elements",
                    "Expand on key concepts",
                    "Include more examples",
                    "Add summary or conclusion",
                ]
            )
        return suggestions

    def _generate_engagement_suggestions(self, score: float) -> List[str]:
        """Generate engagement improvement suggestions."""
        suggestions = []
        if score < 0.6:
            suggestions.extend(
                [
                    "Add interactive elements",
                    "Include more visuals",
                    "Improve content flow",
                    "Add real-world examples",
                ]
            )
        return suggestions

    def _generate_accessibility_suggestions(self, score: float) -> List[str]:
        """Generate accessibility improvement suggestions."""
        suggestions = []
        if score < 0.7:
            suggestions.extend(
                [
                    "Add alt text to images",
                    "Improve color contrast",
                    "Add keyboard navigation",
                    "Include screen reader support",
                ]
            )
        return suggestions
