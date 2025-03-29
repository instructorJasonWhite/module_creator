import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

import fitz  # PyMuPDF for PDF processing
from docx import Document as DocxDocument

from ..schemas.document_schemas import (ContentComplexity, DocumentAnalysis,
                                        DocumentProcessingResult,
                                        DocumentProcessingStatus,
                                        DocumentSection, DocumentType)
from ..schemas.message_schemas import AgentResponse, AgentTask
from .base_agent import BaseAgent


class DocumentAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing educational documents."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supported_types = {
            DocumentType.PDF: self._process_pdf,
            DocumentType.DOCX: self._process_docx,
            DocumentType.TXT: self._process_txt,
        }

    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        Process a document analysis task.
        Args:
            task: The task containing document information
        Returns:
            AgentResponse: The analysis results
        """
        try:
            # Extract document information from task
            document_id = task.task_data.get("document_id")
            file_path = task.task_data.get("file_path")
            doc_type = task.task_data.get("document_type")

            if not all([document_id, file_path, doc_type]):
                raise ValueError("Missing required document information")

            # Process the document
            analysis = await self._analyze_document(document_id, file_path, doc_type)

            # Create processing result
            result = DocumentProcessingResult(
                document_id=document_id,
                status=DocumentProcessingStatus.COMPLETED,
                analysis=analysis,
                completed_at=datetime.utcnow(),
            )

            return AgentResponse(
                task_id=task.message_id, result=result.dict(), error=None
            )

        except Exception as e:
            self.logger.error(f"Document analysis failed: {str(e)}")
            return AgentResponse(task_id=task.message_id, result=None, error=str(e))

    async def _analyze_document(
        self, document_id: UUID, file_path: str, doc_type: DocumentType
    ) -> DocumentAnalysis:
        """
        Analyze a document based on its type.
        Args:
            document_id: UUID of the document
            file_path: Path to the document
            doc_type: Type of document
        Returns:
            DocumentAnalysis: Analysis results
        """
        if doc_type not in self.supported_types:
            raise ValueError(f"Unsupported document type: {doc_type}")

        # Process document using appropriate method
        sections, metadata = await self.supported_types[doc_type](file_path)

        # Analyze content complexity
        overall_complexity = self._analyze_complexity(sections)

        # Extract main topics and key concepts
        main_topics = self._extract_main_topics(sections)
        key_concepts = self._extract_key_concepts(sections)

        # Create document analysis
        return DocumentAnalysis(
            document_id=document_id,
            title=metadata.get("title", "Untitled"),
            document_type=doc_type,
            author=metadata.get("author"),
            creation_date=metadata.get("creation_date"),
            last_modified=metadata.get("last_modified"),
            total_pages=metadata.get("total_pages"),
            sections=sections,
            main_topics=main_topics,
            key_concepts=key_concepts,
            prerequisites=self._identify_prerequisites(sections),
            target_audience=self._determine_target_audience(
                sections, overall_complexity
            ),
            overall_complexity=overall_complexity,
            metadata=metadata,
        )

    async def _process_pdf(
        self, file_path: str
    ) -> tuple[List[DocumentSection], Dict[str, Any]]:
        """Process a PDF document."""
        doc = fitz.open(file_path)
        sections = []
        current_section = None

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if not text:
                                continue

                            # Check if this is a heading
                            font_size = span["size"]
                            if font_size >= 14:  # Assuming headings are larger
                                if current_section:
                                    sections.append(current_section)
                                current_section = DocumentSection(
                                    title=text,
                                    content="",
                                    level=self._determine_heading_level(font_size),
                                    complexity=ContentComplexity.INTERMEDIATE,
                                )
                            elif current_section:
                                current_section.content += text + " "

        if current_section:
            sections.append(current_section)

        metadata = {
            "title": doc.metadata.get("title", "Untitled"),
            "author": doc.metadata.get("author"),
            "creation_date": doc.metadata.get("creationDate"),
            "last_modified": doc.metadata.get("modDate"),
            "total_pages": len(doc),
        }

        doc.close()
        return sections, metadata

    async def _process_docx(
        self, file_path: str
    ) -> tuple[List[DocumentSection], Dict[str, Any]]:
        """Process a DOCX document."""
        doc = DocxDocument(file_path)
        sections = []
        current_section = None

        for paragraph in doc.paragraphs:
            if paragraph.style.name.startswith("Heading"):
                if current_section:
                    sections.append(current_section)
                level = int(paragraph.style.name[-1])
                current_section = DocumentSection(
                    title=paragraph.text,
                    content="",
                    level=level,
                    complexity=ContentComplexity.INTERMEDIATE,
                )
            elif current_section:
                current_section.content += paragraph.text + " "

        if current_section:
            sections.append(current_section)

        metadata = {
            "title": doc.core_properties.title or "Untitled",
            "author": doc.core_properties.author,
            "creation_date": doc.core_properties.created,
            "last_modified": doc.core_properties.modified,
            "total_pages": len(doc.sections),
        }

        return sections, metadata

    async def _process_txt(
        self, file_path: str
    ) -> tuple[List[DocumentSection], Dict[str, Any]]:
        """Process a TXT document."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple section detection based on newlines and common heading patterns
        sections = []
        current_section = DocumentSection(
            title="Main Content",
            content=content,
            level=1,
            complexity=ContentComplexity.INTERMEDIATE,
        )
        sections.append(current_section)

        metadata = {"title": Path(file_path).stem, "total_pages": 1}

        return sections, metadata

    def _determine_heading_level(self, font_size: float) -> int:
        """Determine heading level based on font size."""
        if font_size >= 24:
            return 1
        elif font_size >= 20:
            return 2
        elif font_size >= 16:
            return 3
        elif font_size >= 14:
            return 4
        elif font_size >= 12:
            return 5
        else:
            return 6

    def _analyze_complexity(self, sections: List[DocumentSection]) -> ContentComplexity:
        """Analyze content complexity based on various factors."""
        # Simple complexity analysis based on word length and sentence structure
        total_words = 0
        long_words = 0

        for section in sections:
            words = section.content.split()
            total_words += len(words)
            long_words += sum(1 for word in words if len(word) > 6)

        if total_words == 0:
            return ContentComplexity.BEGINNER

        complexity_ratio = long_words / total_words
        if complexity_ratio < 0.2:
            return ContentComplexity.BEGINNER
        elif complexity_ratio < 0.4:
            return ContentComplexity.INTERMEDIATE
        else:
            return ContentComplexity.ADVANCED

    def _extract_main_topics(self, sections: List[DocumentSection]) -> List[str]:
        """Extract main topics from document sections."""
        topics = []
        for section in sections:
            if section.level <= 2:  # Consider only top-level headings
                topics.append(section.title)
        return topics

    def _extract_key_concepts(self, sections: List[DocumentSection]) -> List[str]:
        """Extract key concepts from document content."""
        concepts = set()
        for section in sections:
            # Look for capitalized phrases and technical terms
            words = section.content.split()
            for i in range(len(words) - 1):
                if words[i][0].isupper() and words[i + 1][0].isupper():
                    concepts.add(f"{words[i]} {words[i + 1]}")
        return list(concepts)

    def _identify_prerequisites(self, sections: List[DocumentSection]) -> List[str]:
        """Identify prerequisites from document content."""
        prerequisites = []
        prerequisite_keywords = [
            "prerequisite",
            "required",
            "before",
            "assume",
            "knowledge",
        ]

        for section in sections:
            content_lower = section.content.lower()
            for keyword in prerequisite_keywords:
                if keyword in content_lower:
                    # Extract the sentence containing the keyword
                    sentences = re.split(r"[.!?]+", section.content)
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            prerequisites.append(sentence.strip())

        return prerequisites

    def _determine_target_audience(
        self, sections: List[DocumentSection], complexity: ContentComplexity
    ) -> str:
        """Determine the target audience based on content complexity and structure."""
        if complexity == ContentComplexity.BEGINNER:
            return "Beginner learners"
        elif complexity == ContentComplexity.INTERMEDIATE:
            return "Intermediate learners"
        else:
            return "Advanced learners"
