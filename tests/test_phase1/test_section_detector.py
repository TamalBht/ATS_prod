"""
Unit tests for section detector
"""

import pytest
from src.parser.section_detector import SectionDetector


class TestSectionDetection:
    """Test section detection functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.detector = SectionDetector()
    
    def test_detect_sections_with_headers(self):
        """Test section detection with clear headers."""
        text = """
EXPERIENCE
Work history here

EDUCATION
School info here

SKILLS
Python, Java
"""
        sections = self.detector.detect_sections(text)
        
        assert 'experience' in sections
        assert 'education' in sections
        assert 'skills' in sections
    
    def test_detect_sections_case_insensitive(self):
        """Test case-insensitive detection."""
        text = """
experience
Work history

Education
School info
"""
        sections = self.detector.detect_sections(text)
        
        assert 'experience' in sections
        assert 'education' in sections
    
    def test_detect_sections_with_variants(self):
        """Test detection of section name variants."""
        text = """
PROFESSIONAL EXPERIENCE
Work history

EDUCATIONAL BACKGROUND
School info

TECHNICAL SKILLS
Python, Java
"""
        sections = self.detector.detect_sections(text)
        
        assert 'experience' in sections
        assert 'education' in sections
        assert 'skills' in sections
    
    def test_detect_sections_empty_text(self):
        """Test with empty text."""
        sections = self.detector.detect_sections("")
        assert len(sections) == 0
    
    def test_detect_sections_no_headers(self):
        """Test with no section headers."""
        text = "Just some random text without headers"
        sections = self.detector.detect_sections(text)
        
        # Should create a summary section with low confidence
        assert 'summary' in sections
        assert sections['summary'].confidence < 1.0
    
    def test_section_content_extraction(self):
        """Test that section content is correctly extracted."""
        text = """
SKILLS
Python
JavaScript
Java

EXPERIENCE
Software Engineer
"""
        sections = self.detector.detect_sections(text)
        
        skills_content = sections['skills'].content
        assert 'Python' in skills_content
        assert 'JavaScript' in skills_content
        assert 'Java' in skills_content


class TestContactExtraction:
    """Test contact information extraction."""
    
    def setup_method(self):
        """Setup for each test."""
        self.detector = SectionDetector()
    
    def test_extract_contact_info_complete(self):
        """Test extraction of complete contact info."""
        text = """
John Doe
john.doe@email.com
(555) 123-4567
linkedin.com/in/johndoe
github.com/johndoe

EXPERIENCE
Work history
"""
        contact = self.detector.extract_contact_info(text)
        
        assert contact.name == "John Doe"
        assert contact.email == "john.doe@email.com"
        assert contact.phone is not None
    
    def test_extract_contact_info_partial(self):
        """Test extraction with partial info."""
        text = """
Jane Smith
jane@example.com

EXPERIENCE
Work history
"""
        contact = self.detector.extract_contact_info(text)
        
        assert contact.name == "Jane Smith"
        assert contact.email == "jane@example.com"
    
    def test_extract_contact_info_no_name(self):
        """Test when name is not clearly identifiable."""
        text = """
Email: contact@example.com
Phone: 555-1234

EXPERIENCE
Work history
"""
        contact = self.detector.extract_contact_info(text)
        
        assert contact.email == "contact@example.com"
        # Name might not be extracted in this case


class TestSkillsExtraction:
    """Test skills extraction."""
    
    def setup_method(self):
        """Setup for each test."""
        self.detector = SectionDetector()
    
    def test_extract_skills_comma_separated(self):
        """Test comma-separated skills."""
        skills_text = "Python, JavaScript, Java, React, Node.js"
        skills = self.detector.extract_skills(skills_text)
        
        assert len(skills) >= 3
        assert "Python" in skills
        assert "JavaScript" in skills
    
    def test_extract_skills_bullet_points(self):
        """Test bullet-pointed skills."""
        skills_text = """
• Python
• JavaScript
• Java
"""
        skills = self.detector.extract_skills(skills_text)
        
        assert len(skills) >= 3
    
    def test_extract_skills_newline_separated(self):
        """Test newline-separated skills."""
        skills_text = """
Python
JavaScript
Java
"""
        skills = self.detector.extract_skills(skills_text)
        
        assert len(skills) >= 3
    
    def test_extract_skills_empty(self):
        """Test with empty skills text."""
        skills = self.detector.extract_skills("")
        assert len(skills) == 0
    
    def test_extract_skills_deduplication(self):
        """Test skill deduplication."""
        skills_text = "Python, JavaScript, Python, Java, JavaScript"
        skills = self.detector.extract_skills(skills_text)
        
        # Should deduplicate
        assert skills.count("Python") == 1
        assert skills.count("JavaScript") == 1
    
    def test_extract_skills_max_limit(self):
        """Test maximum skill limit."""
        # Create text with 100 skills
        skills_text = ", ".join([f"Skill{i}" for i in range(100)])
        skills = self.detector.extract_skills(skills_text)
        
        # Should cap at 50
        assert len(skills) <= 50