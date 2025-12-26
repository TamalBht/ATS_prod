"""
PDF parser implementation
"""

from pathlib import Path
from typing import Optional, Tuple
import pdfplumber
from PyPDF2 import PdfReader

from src.parser.base_parser import BaseParser
from src.utils.text_utils import clean_text


class PDFParser(BaseParser):
    """Parser for PDF files using multiple extraction strategies."""
    
    def supports_file_type(self, file_path: Path) -> bool:
        """Check if file is PDF."""
        return file_path.suffix.lower() == '.pdf'
    
    def parse(self, file_path: Path) -> Optional[str]:
        """
        Parse PDF file and extract text.
        
        Tries multiple extraction methods and returns best result.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text or None if all methods fail
        """
        if not self.validate_file(file_path):
            return None
        
        if not self.supports_file_type(file_path):
            self.logger.error(f"File is not a PDF: {file_path}")
            return None
        
        # Try pdfplumber first (better formatting)
        text_pdfplumber = self._extract_with_pdfplumber(file_path)
        
        # Try PyPDF2 as fallback
        text_pypdf2 = self._extract_with_pypdf2(file_path)
        
        # Choose best result
        text = self._choose_best_extraction(text_pdfplumber, text_pypdf2)
        
        if text:
            self.logger.info(f"Successfully parsed PDF: {file_path.name}")
            return clean_text(text)
        else:
            self.logger.error(f"Failed to extract text from PDF: {file_path}")
            return None
    
    def _extract_with_pdfplumber(self, file_path: Path) -> Optional[str]:
        """
        Extract text using pdfplumber (preserves layout).
        
        Args:
            file_path: Path to PDF
            
        Returns:
            Extracted text or None
        """
        try:
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            text = '\n\n'.join(text_parts)
            self.logger.debug(f"pdfplumber extracted {len(text)} characters")
            return text if text else None
            
        except Exception as e:
            self.logger.warning(f"pdfplumber extraction failed: {e}")
            return None
    
    def _extract_with_pypdf2(self, file_path: Path) -> Optional[str]:
        """
        Extract text using PyPDF2 (more robust).
        
        Args:
            file_path: Path to PDF
            
        Returns:
            Extracted text or None
        """
        try:
            text_parts = []
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            text = '\n\n'.join(text_parts)
            self.logger.debug(f"PyPDF2 extracted {len(text)} characters")
            return text if text else None
            
        except Exception as e:
            self.logger.warning(f"PyPDF2 extraction failed: {e}")
            return None
    
    def _choose_best_extraction(
        self, 
        text1: Optional[str], 
        text2: Optional[str]
    ) -> Optional[str]:
        """
        Choose best extraction result based on quality heuristics.
        
        Args:
            text1: First extraction result
            text2: Second extraction result
            
        Returns:
            Best result
        """
        # If only one worked, use it
        if text1 and not text2:
            return text1
        if text2 and not text1:
            return text2
        if not text1 and not text2:
            return None
        
        # Both worked - choose longer result (usually better)
        # Could add more sophisticated heuristics here
        return text1 if len(text1) >= len(text2) else text2
    
    def get_page_count(self, file_path: Path) -> Optional[int]:
        """
        Get number of pages in PDF.
        
        Args:
            file_path: Path to PDF
            
        Returns:
            Page count or None if error
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages)
        except Exception as e:
            self.logger.warning(f"Could not get page count: {e}")
            return None