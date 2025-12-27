"""
Abstract base scorer for resume scoring components
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from src.models.resume_data import ResumeData
from src.config.settings import get_settings
from src.utils.logger import get_logger


class BaseScorer(ABC):
    """Abstract base class for scoring components."""
    
    def __init__(self):
        """Initialize scorer."""
        self.logger = get_logger(self.__class__.__name__)
        self.settings = get_settings()
        self.config = self._load_scoring_config()
    
    def _load_scoring_config(self) -> Dict[str, Any]:
        """
        Load scoring configuration from settings.
        
        Returns:
            Scoring configuration dictionary
        """
        return self.settings.get('scoring', {})
    
    @abstractmethod
    def calculate_score(self, resume_data: ResumeData) -> float:
        """
        Calculate score for this component.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Score value
        """
        pass
    
    @abstractmethod
    def get_max_score(self) -> float:
        """
        Get maximum possible score for this component.
        
        Returns:
            Maximum score
        """
        pass
    
    def get_feedback(self, resume_data: ResumeData) -> Dict[str, Any]:
        """
        Get feedback for this scoring component.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Dictionary with strengths, weaknesses, suggestions
        """
        return {
            'strengths': [],
            'weaknesses': [],
            'suggestions': []
        }
    
    def _clamp_score(self, score: float, min_val: float = 0.0, max_val: float = None) -> float:
        """
        Clamp score to valid range.
        
        Args:
            score: Raw score
            min_val: Minimum value
            max_val: Maximum value (uses get_max_score if None)
            
        Returns:
            Clamped score
        """
        if max_val is None:
            max_val = self.get_max_score()
        
        return max(min_val, min(max_val, score))