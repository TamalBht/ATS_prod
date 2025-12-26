"""
Abstract base parser for resume file formats
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger


class BaseParser(ABC):
    """Abstract base class for resume parsers."""
    
    def __init__(self):
        """Initialize parser."""
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def parse(self, file_path: Path) -> Optional[str]:
        """
        Parse a file and extract text.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text or None if parsing fails
        """
        pass
    
    @abstractmethod
    def supports_file_type(self, file_path: Path) -> bool:
        """
        Check if parser supports this file type.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported
        """
        pass
    
    def validate_file(self, file_path: Path) -> bool:
        """
        Validate file exists and is readable.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if valid
        """
        if not file_path.exists():
            self.logger.error(f"File does not exist: {file_path}")
            return False
        
        if not file_path.is_file():
            self.logger.error(f"Path is not a file: {file_path}")
            return False
        
        if file_path.stat().st_size == 0:
            self.logger.warning(f"File is empty: {file_path}")
            return False
        
        return True