"""
Resume structure validator for ATS compatibility.
Validates presence and formatting of required sections.
"""

import re
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)


class StructureValidator:
    """
    Validates resume structure for ATS requirements.
    Checks for required sections and proper organization.
    """
    
    def __init__(self):
        """Initialize structure validator."""
        # Required sections for most ATS systems
        self.required_sections = {
            'contact': ['contact', 'contact information', 'personal information'],
            'experience': ['experience', 'work experience', 'professional experience', 'employment'],
            'education': ['education', 'academic background', 'qualifications'],
            'skills': ['skills', 'technical skills', 'core competencies', 'expertise']
        }
        
        # Optional but recommended sections
        self.recommended_sections = {
            'summary': ['summary', 'professional summary', 'profile', 'objective'],
            'certifications': ['certifications', 'certificates', 'licenses'],
            'projects': ['projects', 'key projects', 'portfolio']
        }
    def _section_is_empty(self, parsed_resume, section_type: str) -> bool:
        """
    Returns True if a required section exists but has no meaningful content.
    Handles strings, lists, dicts.
    """
        if section_type not in parsed_resume:
            return True  # treat as missing

        data = parsed_resume.get(section_type)

    # Empty or None
        if data is None:
            return True

    # Empty string or short meaningless text
        if isinstance(data, str):
            return len(data.strip()) < 10

    # Empty list
        if isinstance(data, list):
            return len(data) == 0
    # Empty dict
        if isinstance(data, dict):
            return len(data.keys()) == 0

    # Fallback: convert to string
        return len(str(data).strip()) < 10

    
    def validate_structure(self, parsed_resume: Dict) -> Dict:
        """
        Validate resume structure against ATS requirements.
        
        Args:
            parsed_resume: Parsed resume dictionary from Phase 1
            
        Returns:
            Dict with structure validation results
        """
        issues = []
        score = 100
        
        # Check for required sections
        missing_required = []
        present_required = []
        
        for section_type, section_variants in self.required_sections.items():
            found = self._section_exists(parsed_resume, section_variants) and not self._section_is_empty(parsed_resume, section_type)

            if found:
                present_required.append(section_type)
            else:
                missing_required.append(section_type)
                issues.append({
                    'severity': 'critical' if section_type in ['contact', 'experience'] else 'high',
                    'issue': f'Missing required section: {section_type.upper()}',
                    'impact': 'ATS may reject resume or significantly lower ranking',
                    'recommendation': f'Add a clearly labeled {section_type.upper()} section'
                })
                penalty = 30 if section_type in ['contact', 'experience'] else 20
                score -= penalty
        
        # Check for recommended sections
        missing_recommended = []
        present_recommended = []
        
        for section_type, section_variants in self.recommended_sections.items():
            found = self._section_exists(parsed_resume, section_variants)
            if found:
                present_recommended.append(section_type)
            else:
                missing_recommended.append(section_type)
                if section_type == 'summary':
                    issues.append({
                        'severity': 'medium',
                        'issue': 'Missing professional summary',
                        'impact': 'Reduces keyword matching opportunities',
                        'recommendation': 'Add a 2-3 sentence professional summary at the top'
                    })
                    score -= 10
        
        # Validate section content quality
        content_issues = self._validate_section_content(parsed_resume)
        issues.extend(content_issues['issues'])
        score -= content_issues['penalty']
        
        # Check section ordering
        order_issues = self._validate_section_order(parsed_resume)
        if order_issues:
            issues.extend(order_issues)
            score -= 5
        
        return {
            'structure_score': max(0, round(score, 2)),
            'is_well_structured': score >= 70,
            'required_sections': {
                'present': present_required,
                'missing': missing_required
            },
            'recommended_sections': {
                'present': present_recommended,
                'missing': missing_recommended
            },
            'issues': issues,
            'recommendations': self._generate_structure_recommendations(
                missing_required, missing_recommended, issues
            )
        }
    
    def _section_exists(self, parsed_resume: Dict, section_variants: List[str]) -> bool:
        """Check if any variant of a section exists in parsed resume."""
        sections = parsed_resume.get("sections", {})
        resume_keys_lower = {k.lower().strip() for k in sections.keys()}
        
        for variant in section_variants:
            # Exact match
            if variant in resume_keys_lower:
                return True
            # Partial match
            if any(variant in key for key in resume_keys_lower):
                return True
        
        return False
    
    def _validate_section_content(self, parsed_resume: Dict) -> Dict:
        """Validate that sections have meaningful content."""
        issues = []
        penalty = 0
        
        for section_name, section_data in parsed_resume.items():
            section_lower = section_name.lower()
            
            # Skip metadata sections
            if section_lower in ['metadata', 'raw_text']:
                continue
            
            # Check if section is empty
            is_empty = False
            if isinstance(section_data, str):
                is_empty = len(section_data.strip()) < 10
            elif isinstance(section_data, list):
                is_empty = len(section_data) == 0
            elif isinstance(section_data, dict):
                is_empty = len(section_data) == 0
            
            if is_empty:
                issues.append({
                    'severity': 'medium',
                    'issue': f'Section "{section_name}" is empty or has minimal content',
                    'impact': 'ATS will not extract meaningful information from this section',
                    'recommendation': f'Add substantive content to {section_name} section'
                })
                penalty += 10
            
            # Validate experience section specifically
            if 'experience' in section_lower and isinstance(section_data, list):
                for i, job in enumerate(section_data):
                    if isinstance(job, dict):
                        if 'description' not in job or not job.get('description'):
                            issues.append({
                                'severity': 'medium',
                                'issue': f'Work experience entry #{i+1} missing description',
                                'impact': 'Reduces keyword matching and credibility',
                                'recommendation': 'Add bullet points describing responsibilities and achievements'
                            })
                            penalty += 5
        
        return {
            'issues': issues,
            'penalty': min(penalty, 30)  # Cap penalty
        }
    
    def _validate_section_order(self, parsed_resume: Dict) -> List[Dict]:
        """Validate logical section ordering."""
        issues = []
        
        section_keys = [k.lower() for k in parsed_resume.keys()]
        
        # Contact info should be first (or near first)
        contact_position = None
        for i, key in enumerate(section_keys):
            if any(c in key for c in ['contact', 'personal', 'info']):
                contact_position = i
                break
        
        if contact_position and contact_position > 2:
            issues.append({
                'severity': 'low',
                'issue': 'Contact information not at beginning of resume',
                'impact': 'May delay ATS identification of candidate',
                'recommendation': 'Move contact information to the top of resume'
            })
        
        # Experience should come before education (for experienced professionals)
        exp_position = None
        edu_position = None
        
        for i, key in enumerate(section_keys):
            if 'experience' in key and exp_position is None:
                exp_position = i
            if 'education' in key and edu_position is None:
                edu_position = i
        
        # If both exist and education comes first (and resume has significant experience)
        if exp_position and edu_position and edu_position < exp_position:
            # This is OK for recent graduates, but check if they have experience
            if 'experience' in parsed_resume:
                exp_data = parsed_resume['experience']
                if isinstance(exp_data, list) and len(exp_data) > 1:
                    issues.append({
                        'severity': 'low',
                        'issue': 'Education listed before experience for experienced candidate',
                        'impact': 'Minor - May not align with ATS expectations',
                        'recommendation': 'Consider placing experience before education'
                    })
        
        return issues
    
    def _generate_structure_recommendations(self, missing_required: List[str],
                                           missing_recommended: List[str],
                                           issues: List[Dict]) -> List[str]:
        """Generate actionable structure recommendations."""
        recommendations = []
        
        if missing_required:
            recommendations.append(
                f"CRITICAL: Add missing required sections: {', '.join(missing_required).upper()}"
            )
        
        if 'summary' in missing_recommended:
            recommendations.append(
                "Add a professional summary with key skills and experience highlights"
            )
        
        if any('empty' in i['issue'].lower() for i in issues):
            recommendations.append(
                "Fill in all sections with detailed, relevant information"
            )
        
        if not missing_required and not any(i['severity'] == 'critical' for i in issues):
            recommendations.append(
                "Structure is solid - focus on content quality and keyword optimization"
            )
        
        return recommendations
    
    def check_section_labels(self, text: str) -> Dict:
        """
        Check if section labels are clear and ATS-recognizable.
        
        Args:
            text: Raw resume text
            
        Returns:
            Dict with section label analysis
        """
        issues = []
        score = 100
        
        # Common section label patterns
        standard_labels = [
            'summary', 'objective', 'profile',
        'experience', 'employment', 'work history', 'professional experience',
        'education', 'academic',
        'skills', 'expertise', 'competencies',
        'certifications', 'licenses',
        'projects', 'portfolio'
        ]
        
        # Look for section headers (all caps, followed by content)
        potential_headers = re.findall(r'^([A-Z][A-Z\s&]{2,30})\s*$', text, re.MULTILINE)
        
        found_standard = 0
        non_standard_headers = []
        
        for header in potential_headers:
            header_lower = header.lower().strip()
            if any(label in header_lower for label in standard_labels):
                found_standard += 1
            else:
                non_standard_headers.append(header)
        
        if found_standard < 3:
            text_lower = text.lower()
            detected_labels = {
                label for label in standard_labels if label in text_lower
            }
            found_standard = max(found_standard, len(detected_labels))
            if found_standard < 3:
                issues.append({
                    'severity': 'high',
                    'issue': 'Few standard section labels detected',
                    'impact': 'ATS may not correctly identify resume sections',
                    'recommendation': 'Use clear, standard section headings like "EXPERIENCE", "EDUCATION", "SKILLS"'
            })
            score -= 25
        
        if non_standard_headers:
            issues.append({
                'severity': 'medium',
                'issue': f'Non-standard section labels found: {", ".join(non_standard_headers[:3])}',
                'impact': 'ATS may not recognize these sections',
                'recommendation': 'Use industry-standard section names'
            })
            score -= 15
        
        return {
            'label_score': max(0, score),
            'standard_labels_found': found_standard,
            'non_standard_labels': non_standard_headers,
            'issues': issues
        }