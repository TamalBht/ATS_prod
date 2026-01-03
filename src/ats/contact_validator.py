"""
Contact information validator for ATS compatibility.
Validates and extracts contact details.
"""

import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ContactValidator:
    """
    Validates contact information for ATS compatibility.
    Ensures critical contact details are present and parseable.
    """

    def __init__(self):
        """Initialize contact validator."""
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        self.phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{10}',
        ]

        self.linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        self.website_pattern = r'https?://[\w\-.]+(\.com|\.net|\.org|\.io|\.dev)[\w\-./]*'

    def validate_contact_info(self, parsed_resume: Dict, raw_text: str = "") -> Dict:
        issues = []
        score = 100

        contact_data = self._extract_contact_info(parsed_resume, raw_text)

        if not contact_data['email']:
            issues.append({
                'severity': 'critical',
                'issue': 'No email address found',
                'impact': 'Recruiters cannot contact you - resume may be auto-rejected',
                'recommendation': 'Add a professional email address at the top of resume'
            })
            score -= 40
        elif not self._is_professional_email(contact_data['email']):
            issues.append({
                'severity': 'medium',
                'issue': 'Email address may not be professional',
                'impact': 'May create negative impression',
                'recommendation': 'Use a professional email (firstname.lastname@domain.com)'
            })
            score -= 10

        if not contact_data['phone']:
            issues.append({
                'severity': 'high',
                'issue': 'No phone number found',
                'impact': 'Limits recruiter contact options',
                'recommendation': 'Add a phone number with area code'
            })
            score -= 25

        if not contact_data['name']:
            issues.append({
                'severity': 'critical',
                'issue': 'Name not clearly identified',
                'impact': 'ATS may not properly identify candidate',
                'recommendation': 'Ensure your name is prominently displayed at the top'
            })
            score -= 30

        if not contact_data['linkedin']:
            issues.append({
                'severity': 'low',
                'issue': 'No LinkedIn profile found',
                'impact': 'Missing opportunity for additional professional information',
                'recommendation': 'Consider adding LinkedIn profile URL'
            })
            score -= 5

        if not self._is_contact_at_top(raw_text, contact_data):
            issues.append({
                'severity': 'medium',
                'issue': 'Contact information may not be at top of resume',
                'impact': 'ATS may have difficulty locating contact details',
                'recommendation': 'Place all contact information at the very top of resume'
            })
            score -= 10

        return {
            'contact_score': max(0, round(score, 2)),
            'has_complete_contact': score >= 70,
            'contact_details': contact_data,
            'issues': issues,
            'recommendations': self._generate_contact_recommendations(contact_data, issues)
        }

    def _extract_contact_info(self, parsed_resume: Dict, raw_text: str) -> Dict:
        contact_info = {
            'name': None,
            'email': None,
            'phone': None,
            'linkedin': None,
            'website': None,
            'location': None
        }

        for key, value in parsed_resume.items():
            if 'contact' in key.lower() or 'personal' in key.lower():
                if isinstance(value, dict):
                    contact_info.update({
                        k: v for k, v in value.items()
                        if k in contact_info and v
                    })
                elif isinstance(value, str):
                    self._parse_contact_string(value, contact_info)

        search_text = raw_text if raw_text else str(parsed_resume)

        if not contact_info['email']:
            email_match = re.search(self.email_pattern, search_text)
            if email_match:
                contact_info['email'] = email_match.group()

        if not contact_info['phone']:
            for pattern in self.phone_patterns:
                phone_match = re.search(pattern, search_text)
                if phone_match:
                    contact_info['phone'] = phone_match.group()
                    break

        if not contact_info['linkedin']:
            linkedin_match = re.search(self.linkedin_pattern, search_text, re.IGNORECASE)
            if linkedin_match:
                contact_info['linkedin'] = linkedin_match.group()

        if not contact_info['website']:
            website_match = re.search(self.website_pattern, search_text)
            if website_match:
                contact_info['website'] = website_match.group()

        if not contact_info['name']:
            contact_info['name'] = self._extract_name(raw_text, parsed_resume)

        return contact_info

    def _parse_contact_string(self, contact_string: str, contact_info: Dict):
        email_match = re.search(self.email_pattern, contact_string)
        if email_match:
            contact_info['email'] = email_match.group()

        for pattern in self.phone_patterns:
            phone_match = re.search(pattern, contact_string)
            if phone_match:
                contact_info['phone'] = phone_match.group()
                break

        linkedin_match = re.search(self.linkedin_pattern, contact_string, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()

    def _extract_name(self, raw_text: str, parsed_resume: Dict) -> Optional[str]:
        if not raw_text:
            return None

        first_lines = raw_text.split('\n')[:5]

        for line in first_lines:
            line = line.strip()
            name_match = re.match(
                r'^([A-Z][a-z]{1,20}\s){1,3}[A-Z][a-z]{1,20}$',
                line
            )
            if name_match:
                return line

        return None

    def _is_professional_email(self, email: str) -> bool:
        unprofessional_keywords = [
            'cute', 'sexy', 'hot', 'cool', 'baby', 'love',
            '69', '420', 'gangsta', 'princess', 'rockstar'
        ]

        email_lower = email.lower()
        return not any(keyword in email_lower for keyword in unprofessional_keywords)

    def _is_contact_at_top(self, raw_text: str, contact_data: Dict) -> bool:
        if not raw_text:
            return True

        first_section = '\n'.join(raw_text.split('\n')[:15])

        if contact_data['email'] and contact_data['email'] in first_section:
            return True
        if contact_data['phone'] and contact_data['phone'] in first_section:
            return True

        return False

    def _generate_contact_recommendations(
        self,
        contact_data: Dict,
        issues: List[Dict]
    ) -> List[str]:

        recommendations = []

        if not contact_data['email']:
            recommendations.append(
                "CRITICAL: Add a professional email address (firstname.lastname@domain.com)"
            )

        if not contact_data['phone']:
            recommendations.append(
                "Add phone number with area code in standard format"
            )

        if not contact_data['name']:
            recommendations.append(
                "Ensure your full name is clearly displayed at the top"
            )

        if not contact_data['linkedin']:
            recommendations.append(
                "Consider adding LinkedIn profile for more complete professional presence"
            )

        if contact_data['email'] and not self._is_professional_email(contact_data['email']):
            recommendations.append(
                "Consider using a more professional email address"
            )

        if any(i['severity'] in ['critical', 'high'] for i in issues):
            recommendations.append(
                "Place contact info at top in this format: Name | Phone | Email | LinkedIn"
            )

        return recommendations
