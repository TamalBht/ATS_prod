"""
Unit tests for text utilities
"""

import pytest
from src.utils.text_utils import (
    clean_text, extract_email, extract_phone, extract_urls,
    extract_linkedin, extract_github, count_words,
    normalize_section_name, remove_extra_whitespace
)


class TestTextCleaning:
    """Test text cleaning functions."""
    
    def test_clean_text_removes_null_bytes(self):
        """Test that null bytes are removed."""
        text = "Hello\x00World"
        assert clean_text(text) == "HelloWorld"
    
    def test_clean_text_normalizes_line_endings(self):
        """Test line ending normalization."""
        text = "Line1\r\nLine2\rLine3\nLine4"
        cleaned = clean_text(text)
        assert '\r' not in cleaned
        assert 'Line1\nLine2\nLine3\nLine4' in cleaned
    
    def test_clean_text_removes_excessive_blank_lines(self):
        """Test removal of excessive blank lines."""
        text = "Line1\n\n\n\n\nLine2"
        cleaned = clean_text(text)
        assert '\n\n\n' not in cleaned
    
    def test_clean_text_strips_whitespace(self):
        """Test whitespace stripping."""
        text = "  \n  Text  \n  "
        assert clean_text(text) == "Text"


class TestEmailExtraction:
    """Test email extraction."""
    
    def test_extract_email_simple(self):
        """Test simple email extraction."""
        text = "Contact me at john.doe@example.com for details"
        assert extract_email(text) == "john.doe@example.com"
    
    def test_extract_email_complex(self):
        """Test complex email formats."""
        text = "Email: john.doe+test@sub.example.co.uk"
        email = extract_email(text)
        assert email is not None
        assert '@' in email
    
    def test_extract_email_none(self):
        """Test no email found."""
        text = "No email here"
        assert extract_email(text) is None


class TestPhoneExtraction:
    """Test phone number extraction."""
    
    def test_extract_phone_with_dashes(self):
        """Test phone with dashes."""
        text = "Call 123-456-7890"
        assert extract_phone(text) == "123-456-7890"
    
    def test_extract_phone_with_parentheses(self):
        """Test phone with parentheses."""
        text = "Phone: (123) 456-7890"
        phone = extract_phone(text)
        assert phone is not None
    
    def test_extract_phone_international(self):
        """Test international format."""
        text = "+1-123-456-7890"
        phone = extract_phone(text)
        assert phone is not None
    
    def test_extract_phone_none(self):
        """Test no phone found."""
        text = "No phone here"
        assert extract_phone(text) is None


class TestURLExtraction:
    """Test URL extraction."""
    
    def test_extract_urls_http(self):
        """Test HTTP URL extraction."""
        text = "Visit http://example.com for more"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert "example.com" in urls[0]
    
    def test_extract_urls_https(self):
        """Test HTTPS URL extraction."""
        text = "Visit https://example.com for more"
        urls = extract_urls(text)
        assert len(urls) == 1
    
    def test_extract_linkedin(self):
        """Test LinkedIn URL extraction."""
        text = "Profile: https://linkedin.com/in/johndoe"
        linkedin = extract_linkedin(text)
        assert linkedin is not None
        assert "linkedin.com/in/" in linkedin
    
    def test_extract_github(self):
        """Test GitHub URL extraction."""
        text = "Code: https://github.com/johndoe"
        github = extract_github(text)
        assert github is not None
        assert "github.com/" in github


class TestWordCounting:
    """Test word counting."""
    
    def test_count_words_simple(self):
        """Test simple word count."""
        assert count_words("one two three") == 3
    
    def test_count_words_with_punctuation(self):
        """Test word count with punctuation."""
        assert count_words("Hello, world! How are you?") == 5
    
    def test_count_words_empty(self):
        """Test empty string."""
        assert count_words("") == 1  # split() returns ['']


class TestSectionNameNormalization:
    """Test section name normalization."""
    
    def test_normalize_section_name_lowercase(self):
        """Test lowercase conversion."""
        assert normalize_section_name("EXPERIENCE") == "experience"
    
    def test_normalize_section_name_removes_special_chars(self):
        """Test special character removal."""
        assert normalize_section_name("Work Experience:") == "work experience"
    
    def test_normalize_section_name_removes_extra_spaces(self):
        """Test space normalization."""
        assert normalize_section_name("  Work   Experience  ") == "work experience"


class TestWhitespaceRemoval:
    """Test whitespace removal."""
    
    def test_remove_extra_whitespace_spaces(self):
        """Test multiple space removal."""
        text = "Hello    world"
        assert remove_extra_whitespace(text) == "Hello world"
    
    def test_remove_extra_whitespace_newlines(self):
        """Test multiple newline removal."""
        text = "Line1\n\n\n\nLine2"
        result = remove_extra_whitespace(text)
        assert '\n\n\n' not in result