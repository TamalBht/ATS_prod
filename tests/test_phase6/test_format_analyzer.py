"""
Unit tests for Format Analyzer (Phase 6).
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.ats.format_analyzer import FormatAnalyzer


class TestFormatAnalyzer(unittest.TestCase):
    """Test format analysis functionality."""
    
    def setUp(self):
        """Initialize format analyzer for tests."""
        self.analyzer = FormatAnalyzer()
    
    def test_supported_formats(self):
        """Test supported format detection."""
        self.assertIn('.pdf', self.analyzer.supported_formats)
        self.assertIn('.docx', self.analyzer.supported_formats)
        self.assertIn('.txt', self.analyzer.supported_formats)
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        result = self.analyzer.analyze_file('nonexistent.pdf')
        
        self.assertEqual(result['format_score'], 0)
        self.assertFalse(result['is_ats_friendly'])
        self.assertTrue(any('not found' in issue['issue'].lower() for issue in result['issues']))
    
    def test_unsupported_format(self):
        """Test detection of unsupported file formats."""
        # Create a mock file
        with patch('pathlib.Path.exists', return_value=True):
            result = self.analyzer.analyze_file('resume.xyz')
        
        self.assertEqual(result['format_score'], 0)
        self.assertTrue(any('unsupported' in issue['issue'].lower() for issue in result['issues']))
    
    def test_text_extractability_empty(self):
        """Test extractability analysis with empty text."""
        result = self.analyzer.analyze_text_extractability("")
        
        self.assertEqual(result['extractability_score'], 0)
        self.assertFalse(result['is_extractable'])
    
    def test_text_extractability_good(self):
        """Test extractability analysis with good text."""
        good_text = "This is a well-formatted resume with plenty of content. " * 20
        result = self.analyzer.analyze_text_extractability(good_text)
        
        self.assertGreaterEqual(result['extractability_score'], 80)
        self.assertTrue(result['is_extractable'])
    
    def test_text_extractability_special_chars(self):
        """Test detection of excessive special characters."""
        bad_text = "Resume with ★☆♦♥♣ excessive ✓✗ special ©®™ characters " * 10
        result = self.analyzer.analyze_text_extractability(bad_text)
        
        self.assertLess(result['extractability_score'], 100)
        self.assertTrue(any('special character' in issue['issue'].lower() for issue in result['issues']))


if __name__ == '__main__':
    unittest.main()