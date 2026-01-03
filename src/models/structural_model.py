"""
Structural validation data models for Phase 6.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class IssueSeverity(Enum):
    """Severity levels for ATS compatibility issues."""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class IssueCategory(Enum):
    """Categories of ATS compatibility issues."""
    LAYOUT = "layout"
    FORMATTING = "formatting"
    CONTENT = "content"
    METADATA = "metadata"


@dataclass
class StructuralIssue:
    """Represents a single ATS compatibility issue."""
    category: IssueCategory
    severity: IssueSeverity
    description: str
    location: str
    penalty: int
    recommendation: str
    detected_elements: List[str] = field(default_factory=list)


@dataclass
class StructuralAnalysis:
    """Complete structural analysis results."""
    base_score: int = 100
    total_penalty: int = 0
    final_score: int = 100
    issues: List[StructuralIssue] = field(default_factory=list)
    is_ats_friendly: bool = True
    
    # Detection flags
    has_tables: bool = False
    has_multi_column: bool = False
    has_images: bool = False
    has_text_boxes: bool = False
    has_headers_footers: bool = False
    has_special_chars: bool = False
    
    # Detailed metrics
    num_pages: int = 0
    num_tables: int = 0
    num_images: int = 0
    num_columns_detected: int = 1
    special_char_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "base_score": self.base_score,
            "total_penalty": self.total_penalty,
            "final_score": self.final_score,
            "is_ats_friendly": self.is_ats_friendly,
            "detection_summary": {
                "has_tables": self.has_tables,
                "has_multi_column": self.has_multi_column,
                "has_images": self.has_images,
                "has_text_boxes": self.has_text_boxes,
                "has_headers_footers": self.has_headers_footers,
                "has_special_chars": self.has_special_chars
            },
            "metrics": {
                "num_pages": self.num_pages,
                "num_tables": self.num_tables,
                "num_images": self.num_images,
                "num_columns_detected": self.num_columns_detected,
                "special_char_count": self.special_char_count
            },
            "issues": [
                {
                    "category": issue.category.value,
                    "severity": issue.severity.value,
                    "description": issue.description,
                    "location": issue.location,
                    "penalty": issue.penalty,
                    "recommendation": issue.recommendation,
                    "detected_elements": issue.detected_elements
                }
                for issue in self.issues
            ]
        }