"""
Score data structures and models
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class SectionScore:
    """Score for a single resume section."""
    section_name: str
    score: float
    max_score: float
    present: bool
    content_length: int
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    @property
    def percentage(self) -> float:
        """Get score as percentage."""
        return (self.score / self.max_score * 100) if self.max_score > 0 else 0.0


@dataclass
class CategoryScore:
    """Score for a major category (e.g., Section Completeness)."""
    category_name: str
    score: float
    max_score: float
    details: Dict[str, Any] = field(default_factory=dict)
    breakdown: List[str] = field(default_factory=list)
    
    @property
    def percentage(self) -> float:
        """Get score as percentage."""
        return (self.score / self.max_score * 100) if self.max_score > 0 else 0.0


@dataclass
class ATSScore:
    """Complete ATS scoring results."""
    
    # Overall score
    total_score: float  # 0-100
    max_score: float = 100.0
    
    # Category scores
    section_completeness: CategoryScore = None
    content_quality: CategoryScore = None
    contact_information: CategoryScore = None
    structure_organization: CategoryScore = None
    
    # Section-wise breakdown
    section_scores: Dict[str, SectionScore] = field(default_factory=dict)
    
    # Feedback
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    # Metadata
    scoring_metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'total_score': round(self.total_score, 2),
            'max_score': self.max_score,
            'percentage': round(self.percentage, 2),
            'grade': self.grade,
            'categories': {
                'section_completeness': asdict(self.section_completeness) if self.section_completeness else None,
                'content_quality': asdict(self.content_quality) if self.content_quality else None,
                'contact_information': asdict(self.contact_information) if self.contact_information else None,
                'structure_organization': asdict(self.structure_organization) if self.structure_organization else None,
            },
            'section_scores': {
                k: asdict(v) for k, v in self.section_scores.items()
            },
            'feedback': {
                'strengths': self.strengths,
                'weaknesses': self.weaknesses,
                'suggestions': self.suggestions
            },
            'metadata': self.scoring_metadata
        }
        return result
    
    @property
    def percentage(self) -> float:
        """Get total score as percentage."""
        return (self.total_score / self.max_score * 100) if self.max_score > 0 else 0.0
    
    @property
    def grade(self) -> str:
        """Get letter grade based on score."""
        percentage = self.percentage
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def add_strength(self, strength: str) -> None:
        """Add a strength."""
        if strength not in self.strengths:
            self.strengths.append(strength)
    
    def add_weakness(self, weakness: str) -> None:
        """Add a weakness."""
        if weakness not in self.weaknesses:
            self.weaknesses.append(weakness)
    
    def add_suggestion(self, suggestion: str) -> None:
        """Add a suggestion."""
        if suggestion not in self.suggestions:
            self.suggestions.append(suggestion)