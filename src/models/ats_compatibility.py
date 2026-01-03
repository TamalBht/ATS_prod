"""
ATS Compatibility Data Model - Phase 6
Represents structural analysis results and ATS parsing risks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class RiskLevel(Enum):
    """ATS Compatibility Risk Levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class WarningType(Enum):
    """Categories of ATS compatibility warnings"""
    TABLES = "TABLES"
    MULTI_COLUMN = "MULTI_COLUMN"
    IMAGES = "IMAGES"
    HEADERS_FOOTERS = "HEADERS_FOOTERS"
    TEXT_BOXES = "TEXT_BOXES"
    UNUSUAL_STRUCTURE = "UNUSUAL_STRUCTURE"
    SECTION_ORDER = "SECTION_ORDER"


@dataclass
class CompatibilityWarning:
    """Individual ATS compatibility warning"""
    type: str  # WarningType value
    severity: str  # RiskLevel value
    message: str
    location: Optional[str] = None
    impact: str = ""
    recommendation: str = ""


@dataclass
class LayoutIssue:
    """Detected layout-related issue"""
    issue_type: str
    page_number: Optional[int] = None
    count: int = 1
    details: Dict = field(default_factory=dict)


@dataclass
class ATSCompatibilityResult:
    """Complete ATS compatibility analysis result"""
    risk_level: str  # RiskLevel value
    overall_score: float  # 0-100, where 100 = perfectly compatible
    warnings: List[CompatibilityWarning] = field(default_factory=list)
    layout_issues: List[LayoutIssue] = field(default_factory=list)
    
    # Structural metrics
    has_tables: bool = False
    has_multi_column: bool = False
    has_images: bool = False
    has_headers_footers: bool = False
    has_text_boxes: bool = False
    
    # Section analysis
    section_order_valid: bool = True
    missing_standard_sections: List[str] = field(default_factory=list)
    
    # Metadata
    file_format: str = ""
    total_pages: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary"""
        return {
            "risk_level": self.risk_level,
            "overall_score": round(self.overall_score, 2),
            "warnings": [
                {
                    "type": w.type,
                    "severity": w.severity,
                    "message": w.message,
                    "location": w.location,
                    "impact": w.impact,
                    "recommendation": w.recommendation
                }
                for w in self.warnings
            ],
            "layout_issues": [
                {
                    "issue_type": issue.issue_type,
                    "page_number": issue.page_number,
                    "count": issue.count,
                    "details": issue.details
                }
                for issue in self.layout_issues
            ],
            "structural_flags": {
                "has_tables": self.has_tables,
                "has_multi_column": self.has_multi_column,
                "has_images": self.has_images,
                "has_headers_footers": self.has_headers_footers,
                "has_text_boxes": self.has_text_boxes
            },
            "section_analysis": {
                "section_order_valid": self.section_order_valid,
                "missing_standard_sections": self.missing_standard_sections
            },
            "metadata": {
                "file_format": self.file_format,
                "total_pages": self.total_pages
            }
        }