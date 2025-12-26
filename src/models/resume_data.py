"""
Resume data structures and models
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


@dataclass
class ContactInfo:
    """Contact information extracted from resume."""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    location: Optional[str] = None
    name: Optional[str] = None


@dataclass
class Section:
    """Represents a resume section."""
    title: str
    content: str
    confidence: float = 1.0  # 0.0 to 1.0
    start_index: int = 0
    end_index: int = 0


@dataclass
class ResumeMetadata:
    """Metadata about the parsing process."""
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    parsed_at: str
    parsing_time_ms: float
    total_pages: Optional[int] = None
    total_characters: int = 0
    total_words: int = 0
    warnings: List[str] = field(default_factory=list)
    parsing_confidence: float = 1.0


@dataclass
class ResumeData:
    """Complete structured resume data."""
    
    # Core sections
    contact: ContactInfo = field(default_factory=ContactInfo)
    summary: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    experience: List[Dict[str, Any]] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    
    # Raw data
    raw_text: str = ""
    sections: Dict[str, Section] = field(default_factory=dict)
    
    # Metadata
    metadata: Optional[ResumeMetadata] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        
        # Convert Section objects to dicts
        if 'sections' in result:
            result['sections'] = {
                k: asdict(v) for k, v in self.sections.items()
            }
        
        return result
    
    def get_section_text(self, section_name: str) -> Optional[str]:
        """Get text content of a section by name."""
        section = self.sections.get(section_name.lower())
        return section.content if section else None
    
    def has_section(self, section_name: str) -> bool:
        """Check if a section exists."""
        return section_name.lower() in self.sections
    
    def get_all_section_names(self) -> List[str]:
        """Get list of all detected section names."""
        return list(self.sections.keys())
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to metadata."""
        if self.metadata:
            self.metadata.warnings.append(warning)