"""
Unit tests for resume parser
"""

import pytest
from pathlib import Path
from src.parser.resume_parser import ResumeParser, ParsingError
from src.models.resume_data import ResumeData


@pytest.fixture
def sample_resume_text(tmp_path):
    """Create a sample resume text file."""
    resume_file = tmp_path / "sample_resume.txt"
    content = """
John Doe
john.doe@email.com | (555) 123-4567

SUMMARY
Senior Software Engineer with 5 years of experience.

SKILLS
Python, JavaScript, React, Django

EXPERIENCE
Senior Software Engineer | Tech Corp | 2021 - Present
- Led development of microservices

EDUCATION
BS in Computer Science | University | 2019

PROJECTS
E-Commerce Platform
- Built with React and Django
"""
    resume_file.write_text(content)
    return resume_file


class TestResumeParser:
    """Test resume parser functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.parser = ResumeParser()
    
    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        assert self.parser.pdf_parser is not None
        assert self.parser.docx_parser is not None
        assert self.parser.section_detector is not None
    
    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file raises error."""
        with pytest.raises(ParsingError, match="File not found"):
            self.parser.parse("nonexistent.pdf")
    
    def test_parse_unsupported_format(self, tmp_path):
        """Test unsupported file format raises error."""
        unsupported_file = tmp_path / "test.xyz"
        unsupported_file.write_text("content")
        
        with pytest.raises(ParsingError, match="Unsupported file type"):
            self.parser.parse(unsupported_file)
    
    def test_get_parser_pdf(self, tmp_path):
        """Test PDF parser selection."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.touch()
        
        parser = self.parser._get_parser(pdf_file)
        assert parser == self.parser.pdf_parser
    
    def test_get_parser_docx(self, tmp_path):
        """Test DOCX parser selection."""
        docx_file = tmp_path / "test.docx"
        docx_file.touch()
        
        parser = self.parser._get_parser(docx_file)
        assert parser == self.parser.docx_parser
    
    def test_get_parser_unsupported(self, tmp_path):
        """Test unsupported file returns None."""
        txt_file = tmp_path / "test.txt"
        txt_file.touch()
        
        parser = self.parser._get_parser(txt_file)
        assert parser is None


class TestResumeDataExtraction:
    """Test data extraction from parsed resume."""
    
    def setup_method(self):
        """Setup for each test."""
        self.parser = ResumeParser()
    
    def test_extract_structured_data_creates_contact(self):
        """Test contact info extraction."""
        resume_data = ResumeData(raw_text="john@example.com\n(555) 123-4567")
        self.parser._extract_structured_data(resume_data)
        
        assert resume_data.contact is not None
        assert resume_data.contact.email == "john@example.com"
    
    def test_extract_structured_data_creates_summary(self):
        """Test summary extraction."""
        from src.models.resume_data import Section
        
        resume_data = ResumeData()
        resume_data.sections = {
            'summary': Section(
                title='summary',
                content='I am a software engineer.'
            )
        }
        
        self.parser._extract_structured_data(resume_data)
        
        assert resume_data.summary == 'I am a software engineer.'
    
    def test_extract_structured_data_creates_skills(self):
        """Test skills extraction."""
        from src.models.resume_data import Section
        
        resume_data = ResumeData()
        resume_data.sections = {
            'skills': Section(
                title='skills',
                content='Python, JavaScript, React'
            )
        }
        
        self.parser._extract_structured_data(resume_data)
        
        assert len(resume_data.skills) > 0


class TestMetadataCreation:
    """Test metadata creation."""
    
    def setup_method(self):
        """Setup for each test."""
        self.parser = ResumeParser()
    
    def test_create_metadata_basic_fields(self, tmp_path):
        """Test basic metadata fields."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Sample resume text")
        
        metadata = self.parser._create_metadata(
            test_file,
            "Sample resume text",
            100.0,
            self.parser.pdf_parser
        )
        
        assert metadata.file_name == "test.txt"
        assert metadata.file_type == ".txt"
        assert metadata.file_size > 0
        assert metadata.parsing_time_ms == 100.0
        assert metadata.total_characters == 18
        assert metadata.total_words > 0
    
    def test_calculate_parsing_confidence_high(self):
        """Test high confidence for good text."""
        text = "This is a well-formatted resume with plenty of content."
        confidence = self.parser._calculate_parsing_confidence(text)
        
        assert confidence > 0.8
    
    def test_calculate_parsing_confidence_low_for_short_text(self):
        """Test low confidence for very short text."""
        text = "Short"
        confidence = self.parser._calculate_parsing_confidence(text)
        
        assert confidence < 0.7
    
    def test_calculate_parsing_confidence_empty(self):
        """Test zero confidence for empty text."""
        confidence = self.parser._calculate_parsing_confidence("")
        assert confidence == 0.0


class TestResumeDataModel:
    """Test ResumeData model functionality."""
    
    def test_resume_data_to_dict(self):
        """Test conversion to dictionary."""
        from src.models.resume_data import ResumeData, ContactInfo
        
        resume = ResumeData(
            contact=ContactInfo(email="test@example.com"),
            summary="Test summary",
            skills=["Python", "Java"]
        )
        
        data_dict = resume.to_dict()
        
        assert isinstance(data_dict, dict)
        assert data_dict['contact']['email'] == "test@example.com"
        assert data_dict['summary'] == "Test summary"
        assert len(data_dict['skills']) == 2
    
    def test_get_section_text(self):
        """Test getting section text."""
        from src.models.resume_data import ResumeData, Section
        
        resume = ResumeData()
        resume.sections = {
            'summary': Section(title='summary', content='Test content')
        }
        
        assert resume.get_section_text('summary') == 'Test content'
        assert resume.get_section_text('nonexistent') is None
    
    def test_has_section(self):
        """Test section existence check."""
        from src.models.resume_data import ResumeData, Section
        
        resume = ResumeData()
        resume.sections = {
            'summary': Section(title='summary', content='Test')
        }
        
        assert resume.has_section('summary') is True
        assert resume.has_section('experience') is False
    
    def test_get_all_section_names(self):
        """Test getting all section names."""
        from src.models.resume_data import ResumeData, Section
        
        resume = ResumeData()
        resume.sections = {
            'summary': Section(title='summary', content='Test'),
            'skills': Section(title='skills', content='Python')
        }
        
        names = resume.get_all_section_names()
        assert 'summary' in names
        assert 'skills' in names