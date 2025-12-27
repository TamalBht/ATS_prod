"""
Contact information scoring
"""

from typing import Dict, List

from src.scoring.base_scorer import BaseScorer
from src.models.resume_data import ResumeData
from src.models.score_data import CategoryScore


class ContactScorer(BaseScorer):
    """Scores resume based on contact information completeness."""
    
    def get_max_score(self) -> float:
        """Get maximum contact information score."""
        return self.config.get('max_scores', {}).get('contact_information', 20)
    
    def calculate_score(self, resume_data: ResumeData) -> float:
        """
        Calculate contact information score.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Contact information score
        """
        contact = resume_data.contact
        contact_scores = self.config.get('contact_scores', {})
        
        score = 0.0
        
        # Email (required)
        if contact.email:
            score += contact_scores.get('email', 10)
        
        # Phone (important)
        if contact.phone:
            score += contact_scores.get('phone', 5)
        
        # LinkedIn (bonus)
        if contact.linkedin:
            score += contact_scores.get('linkedin', 3)
        
        # GitHub (bonus)
        if contact.github:
            score += contact_scores.get('github', 2)
        
        return self._clamp_score(score)
    
    def get_category_score(self, resume_data: ResumeData) -> CategoryScore:
        """
        Get category score with details.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            CategoryScore object
        """
        score = self.calculate_score(resume_data)
        contact = resume_data.contact
        contact_scores = self.config.get('contact_scores', {})
        
        breakdown = []
        
        # Email
        email_score = contact_scores.get('email', 10) if contact.email else 0
        breakdown.append(f"Email: {email_score}/{contact_scores.get('email', 10)}")
        
        # Phone
        phone_score = contact_scores.get('phone', 5) if contact.phone else 0
        breakdown.append(f"Phone: {phone_score}/{contact_scores.get('phone', 5)}")
        
        # LinkedIn
        linkedin_score = contact_scores.get('linkedin', 3) if contact.linkedin else 0
        breakdown.append(f"LinkedIn: {linkedin_score}/{contact_scores.get('linkedin', 3)}")
        
        # GitHub
        github_score = contact_scores.get('github', 2) if contact.github else 0
        breakdown.append(f"GitHub: {github_score}/{contact_scores.get('github', 2)}")
        
        return CategoryScore(
            category_name="Contact Information",
            score=score,
            max_score=self.get_max_score(),
            details={
                'has_email': bool(contact.email),
                'has_phone': bool(contact.phone),
                'has_linkedin': bool(contact.linkedin),
                'has_github': bool(contact.github),
                'has_name': bool(contact.name)
            },
            breakdown=breakdown
        )
    
    def get_feedback(self, resume_data: ResumeData) -> Dict[str, List[str]]:
        """
        Get feedback on contact information.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Feedback dictionary
        """
        strengths = []
        weaknesses = []
        suggestions = []
        
        contact = resume_data.contact
        
        # Email (required)
        if contact.email:
            strengths.append("Email address provided")
        else:
            weaknesses.append("Missing email address (required)")
            suggestions.append("Add your professional email address at the top of your resume")
        
        # Phone
        if contact.phone:
            strengths.append("Phone number provided")
        else:
            suggestions.append("Consider adding your phone number for easier contact")
        
        # LinkedIn
        if contact.linkedin:
            strengths.append("LinkedIn profile included")
        else:
            suggestions.append("Add your LinkedIn profile URL to increase professional credibility")
        
        # GitHub (especially relevant for technical roles)
        if contact.github:
            strengths.append("GitHub profile included - great for technical roles")
        else:
            suggestions.append("If you have technical projects, include your GitHub profile URL")
        
        # Name
        if not contact.name:
            weaknesses.append("Name not clearly identified")
            suggestions.append("Ensure your full name appears prominently at the top of your resume")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions
        }