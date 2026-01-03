"""
Unit tests for Structure Validator (Phase 6).
"""

import unittest
from src.ats.structure_validator import StructureValidator


class TestStructureValidator(unittest.TestCase):
    """Test structure validation functionality."""
    
    def setUp(self):
        """Initialize structure validator for tests."""
        self.validator = StructureValidator()
    
    def test_all_required_sections_present(self):
        """Test validation with all required sections."""
        resume = {
            'contact': {'email': 'test@test.com'},
            'experience': [{'title': 'Engineer'}],
            'education': [{'degree': 'BS'}],
            'skills': ['Python', 'Java']
        }
        
        result = self.validator.validate_structure(resume)
        
        self.assertGreaterEqual(result['structure_score'], 70)
        self.assertTrue(result['is_well_structured'])
        self.assertEqual(len(result['required_sections']['missing']), 0)
    
    def test_missing_required_sections(self):
        """Test detection of missing required sections."""
        resume = {
            'skills': ['Python']
        }
        
        result = self.validator.validate_structure(resume)
        
        self.assertLess(result['structure_score'], 70)
        self.assertGreater(len(result['required_sections']['missing']), 0)
        self.assertTrue(any(issue['severity'] in ['critical', 'high'] for issue in result['issues']))
    
    def test_empty_section_detection(self):
        """Test detection of empty sections."""
        resume = {
            'contact': {'email': 'test@test.com'},
            'experience': [],  # Empty
            'education': [{'degree': 'BS'}],
            'skills': ['Python']
        }
        
        result = self.validator.validate_structure(resume)
        
        self.assertLess(result['structure_score'], 100)
        self.assertTrue(any('empty' in issue['issue'].lower() for issue in result['issues']))
    
    def test_section_label_check(self):
        """Test section label analysis."""
        text = """
        PROFESSIONAL EXPERIENCE
        Software Engineer at Tech Corp
        
        EDUCATION
        BS Computer Science
        
        SKILLS
        Python, Java, AWS
        """
        
        result = self.validator.check_section_labels(text)
        
        self.assertGreaterEqual(result['label_score'], 70)
        self.assertGreaterEqual(result['standard_labels_found'], 3)


if __name__ == '__main__':
    unittest.main()