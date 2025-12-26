"""
Section detection for resume parsing
"""

import re
from typing import Dict, List, Tuple, Optional

from src.models.resume_data import Section, ContactInfo
from src.utils.text_utils import (
    extract_email, extract_phone, extract_linkedin, 
    extract_github, normalize_section_name
)
from src.utils.logger import get_logger


class SectionDetector:
    """Detects and extracts sections from resume text."""
    
    # Section header patterns (case-insensitive)
    SECTION_PATTERNS = {
        'summary': [
            r'^summary\s*$',
            r'^professional\s+summary\s*$',
            r'^executive\s+summary\s*$',
            r'^profile\s*$',
            r'^about\s+me\s*$',
            r'^objective\s*$',
        ],
        'experience': [
            r'^experience\s*$',
            r'^work\s+experience\s*$',
            r'^professional\s+experience\s*$',
            r'^employment\s+history\s*$',
            r'^career\s+history\s*$',
        ],
        'education': [
            r'^education\s*$',
            r'^educational\s+background\s*$',
            r'^academic\s+background\s*$',
            r'^qualifications\s*$',
        ],
        'skills': [
            r'^skills\s*$',
            r'^technical\s+skills\s*$',
            r'^core\s+competencies\s*$',
            r'^technologies\s*$',
            r'^expertise\s*$',
        ],
        'projects': [
            r'^projects\s*$',
            r'^key\s+projects\s*$',
            r'^notable\s+projects\s*$',
            r'^project\s+experience\s*$',
        ],
        'certifications': [
            r'^certifications\s*$',
            r'^certificates\s*$',
            r'^licenses\s+and\s+certifications\s*$',
        ],
    }
    
    def __init__(self):
        """Initialize section detector."""
        self.logger = get_logger(__name__)
    
    def detect_sections(self, text: str) -> Dict[str, Section]:
        """
        Detect and extract sections from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary mapping section names to Section objects
        """
        if not text:
            return {}
        
        lines = text.split('\n')
        sections = {}
        
        # Find section boundaries
        section_positions = self._find_section_headers(lines)
        
        if not section_positions:
            self.logger.warning("No section headers detected")
            # If no sections found, treat entire text as summary
            sections['summary'] = Section(
                title='summary',
                content=text.strip(),
                confidence=0.5,
                start_index=0,
                end_index=len(text)
            )
            return sections
        
        # Extract content for each section
        for i, (section_name, line_idx) in enumerate(section_positions):
            # Determine end of section (start of next section or end of text)
            if i < len(section_positions) - 1:
                next_line_idx = section_positions[i + 1][1]
            else:
                next_line_idx = len(lines)
            
            # Extract section content
            section_lines = lines[line_idx + 1:next_line_idx]
            content = '\n'.join(section_lines).strip()
            
            if content:
                sections[section_name] = Section(
                    title=section_name,
                    content=content,
                    confidence=1.0,
                    start_index=line_idx,
                    end_index=next_line_idx
                )
        
        self.logger.info(f"Detected {len(sections)} sections: {list(sections.keys())}")
        return sections
    
    def _find_section_headers(self, lines: List[str]) -> List[Tuple[str, int]]:
        """
        Find section headers in text lines.
        
        Args:
            lines: List of text lines
            
        Returns:
            List of (section_name, line_index) tuples
        """
        section_positions = []
        
        for idx, line in enumerate(lines):
            line_normalized = normalize_section_name(line)
            
            # Check against all section patterns
            for section_name, patterns in self.SECTION_PATTERNS.items():
                for pattern in patterns:
                    if re.match(pattern, line_normalized, re.IGNORECASE):
                        section_positions.append((section_name, idx))
                        break
                else:
                    continue
                break
        
        return section_positions
    
    def extract_contact_info(self, text: str) -> ContactInfo:
        """
        Extract contact information from text.
        
        Typically looks in first 20% of document.
        
        Args:
            text: Resume text
            
        Returns:
            ContactInfo object
        """
        # Focus on top portion of resume (first ~500 chars or 20%)
        search_text = text[:max(500, len(text) // 5)]
        
        contact = ContactInfo(
            email=extract_email(search_text),
            phone=extract_phone(search_text),
            linkedin=extract_linkedin(text),  # Search full text for URLs
            github=extract_github(text),
        )
        
        # Try to extract name (usually first non-empty line)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # First line is often the name if it's short and not email/phone
            first_line = lines[0]
            if (len(first_line.split()) <= 4 and 
                not extract_email(first_line) and 
                not extract_phone(first_line)):
                contact.name = first_line
        
        return contact
    
    def extract_skills(self, skills_text: str) -> List[str]:
        """
        Extract individual skills from skills section.
        
        Args:
            skills_text: Text from skills section
            
        Returns:
            List of skills
        """
        if not skills_text:
            return []
        
        skills = []
        
        # Try different delimiters
        delimiters = [',', '•', '|', '\n', ';']
        
        for delimiter in delimiters:
            if delimiter in skills_text:
                parts = skills_text.split(delimiter)
                potential_skills = [p.strip() for p in parts if p.strip()]
                
                # If we got reasonable results, use them
                if 3 <= len(potential_skills) <= 50:
                    skills = potential_skills
                    break
        
        # Fallback: split by whitespace if no delimiter found
        if not skills:
            skills = skills_text.split()
        
        # Clean and deduplicate
        skills = list(set([s.strip('•-*') for s in skills if len(s.strip()) > 1]))
        
        return skills[:50]  # Cap at 50 skills