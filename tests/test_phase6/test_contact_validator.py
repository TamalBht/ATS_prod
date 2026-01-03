"""
Unit tests for Contact Validator (Phase 6).
"""

from unicodedata import name
import unittest
from src.ats.contact_validator import ContactValidator


class TestContactValidator(unittest.TestCase):
    """Test contact validation functionality."""
    
    def setUp(self):
        """Initialize contact validator for tests."""
        self.validator = ContactValidator()
    
    def test_email_extraction(self):
        """Test email address extraction."""
        text = "Contact me at john.doe@email.com for opportunities"
        contact_info = self.validator._extract_contact_info({}, text)
        
        self.assertEqual(contact_info['email'], 'john.doe@email.com')
    
    def test_phone_extraction(self):
        """Test phone number extraction (various formats)."""
        test_cases = [
            ("Call me at (555) 123-4567", "(555) 123-4567"),
            ("Phone: 555-123-4567", "555-123-4567"),
            ("Mobile: 5551234567", "5551234567")
        ]
        
        for text, expected in test_cases:
            contact_info = self.validator._extract_contact_info({}, text)
            self.assertIsNotNone(contact_info['phone'])
    
    def test_professional_email_check(self):
        """Test professional email detection."""
        self.assertTrue(self.validator._is_professional_email('john.doe@email.com'))
        self.assertTrue(self.validator._is_professional_email('j.doe@company.com'))
        self.assertFalse(self.validator._is_professional_email('coolguy69@email.com'))
        self.assertFalse(self.validator._is_professional_email('sexybaby@email.com'))
    
    def test_complete_contact_validation(self):
        """Test complete contact validation."""
        resume = {
            'contact': {
                'name': 'John Doe',
                'email': 'john.doe@email.com',
                'phone': '(555) 123-4567'
            }
        }
        
        result = self.validator.validate_contact_info(resume, "")
        
        self.assertGreaterEqual(result['contact_score'], 70)
        self.assertTrue(result['has_complete_contact'])
    
    def test_missing_critical_contact(self):
        """Test detection of missing critical contact info."""
        resume = {} # No contact info
        result = self.validator.validate_contact_info(resume, "")
        self.assertLess(result['contact_score'], 70)
        self.assertFalse(result['has_complete_contact'])
        self.assertTrue(any(issue['severity'] == 'critical' for issue in result['issues']))
    def test_linkedin_extraction(self):
        """Test LinkedIn profile extraction."""
        text = "Find me on linkedin.com/in/johndoe"
        contact_info = self.validator._extract_contact_info({}, text)
        self.assertIn('linkedin.com/in/johndoe', contact_info['linkedin'])
    if __name__ == '__main__':
        unittest.main()