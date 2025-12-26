"""
Main resume parser orchestrator
"""

import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.parser.pdf_parser import PDFParser
from src.parser.docx_parser import DOCXParser
from src.parser.section_detector import SectionDetector
from src.models.resume_data import ResumeData, ResumeMetadata
from src.utils.text_utils import count_words
from src.utils.logger import get_logger
from src.utils.exceptions import ATSScorerException


class ParsingError(ATSScorerException):
    """Raised when resume parsing fails."""
    pass


class ResumeParser:
    """Main orchestrator for parsing resumes."""
    
    def __init__(self):
        """Initialize resume parser."""
        self.logger = get_logger(__name__)
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.section_detector = SectionDetector()
    
    def parse(self, file_path: str | Path) -> ResumeData:
        """
        Parse a resume file.
        
        Args:
            file_path: Path to resume file (PDF or DOCX)
            
        Returns:
            ResumeData object with parsed content
            
        Raises:
            ParsingError: If parsing fails
        """
        file_path = Path(file_path)
        start_time = time.time()
        
        self.logger.info(f"Starting parse of {file_path.name}")
        
        # Validate file
        if not file_path.exists():
            raise ParsingError(f"File not found: {file_path}")
        
        # Select appropriate parser
        parser = self._get_parser(file_path)
        if not parser:
            raise ParsingError(f"Unsupported file type: {file_path.suffix}")
        
        # Extract text
        raw_text = parser.parse(file_path)
        if not raw_text:
            raise ParsingError(f"Failed to extract text from {file_path.name}")
        
        # Create resume data
        resume_data = ResumeData(raw_text=raw_text)
        
        # Detect sections
        sections = self.section_detector.detect_sections(raw_text)
        resume_data.sections = sections
        
        # Extract structured data
        self._extract_structured_data(resume_data)
        
        # Create metadata
        parsing_time = (time.time() - start_time) * 1000  # ms
        resume_data.metadata = self._create_metadata(
            file_path, raw_text, parsing_time, parser
        )
        
        self.logger.info(
            f"Successfully parsed {file_path.name} "
            f"({len(sections)} sections, {parsing_time:.2f}ms)"
        )
        
        return resume_data
    
    def _get_parser(self, file_path: Path):
        """
        Get appropriate parser for file type.
        
        Args:
            file_path: Path to file
            
        Returns:
            Parser instance or None
        """
        if self.pdf_parser.supports_file_type(file_path):
            return self.pdf_parser
        elif self.docx_parser.supports_file_type(file_path):
            return self.docx_parser
        else:
            return None
    
    def _extract_structured_data(self, resume_data: ResumeData) -> None:
        """
        Extract structured data from sections.
        
        Args:
            resume_data: ResumeData object to populate
        """
        # Extract contact info
        resume_data.contact = self.section_detector.extract_contact_info(
            resume_data.raw_text
        )
        
        # Extract summary
        if 'summary' in resume_data.sections:
            resume_data.summary = resume_data.sections['summary'].content
        
        # Extract skills
        if 'skills' in resume_data.sections:
            skills_text = resume_data.sections['skills'].content
            resume_data.skills = self.section_detector.extract_skills(skills_text)
        
        # Note: Experience, Education, Projects parsing will be enhanced in later phases
        # For now, we store raw section content
        if 'experience' in resume_data.sections:
            resume_data.experience = [{
                'raw_content': resume_data.sections['experience'].content
            }]
        
        if 'education' in resume_data.sections:
            resume_data.education = [{
                'raw_content': resume_data.sections['education'].content
            }]
        
        if 'projects' in resume_data.sections:
            resume_data.projects = [{
                'raw_content': resume_data.sections['projects'].content
            }]
    
    def _create_metadata(
        self,
        file_path: Path,
        text: str,
        parsing_time: float,
        parser
    ) -> ResumeMetadata:
        """
        Create metadata for parsed resume.
        
        Args:
            file_path: Path to file
            text: Extracted text
            parsing_time: Time taken to parse (ms)
            parser: Parser instance used
            
        Returns:
            ResumeMetadata object
        """
        # Get page count if PDF
        page_count = None
        if isinstance(parser, PDFParser):
            page_count = parser.get_page_count(file_path)
        
        return ResumeMetadata(
            file_path=str(file_path),
            file_name=file_path.name,
            file_size=file_path.stat().st_size,
            file_type=file_path.suffix,
            parsed_at=datetime.now().isoformat(),
            parsing_time_ms=parsing_time,
            total_pages=page_count,
            total_characters=len(text),
            total_words=count_words(text),
            parsing_confidence=self._calculate_parsing_confidence(text)
        )
    
    def _calculate_parsing_confidence(self, text: str) -> float:
        """
        Calculate confidence score for parsing quality.
        
        Args:
            text: Extracted text
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not text:
            return 0.0
        
        confidence = 1.0
        
        # Reduce confidence if text is very short
        if len(text) < 30:
            confidence *= 0.5
        
        # Reduce confidence if text has too many special characters
        # (might indicate poor extraction)
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            confidence *= 0.7
        
        return max(0.0, min(1.0, confidence))