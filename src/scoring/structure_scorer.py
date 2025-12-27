"""
Structure and organization scoring
"""

from typing import Dict, List

from src.scoring.base_scorer import BaseScorer
from src.models.resume_data import ResumeData
from src.models.score_data import CategoryScore


class StructureScorer(BaseScorer):
    """Scores resume based on structure and organization."""
    
    # Recommended section order
    PREFERRED_ORDER = ['summary', 'skills', 'experience', 'education', 'projects', 'certifications']
    
    def get_max_score(self) -> float:
        """Get maximum structure score."""
        return self.config.get('max_scores', {}).get('structure_organization', 10)
    
    def calculate_score(self, resume_data: ResumeData) -> float:
        """
        Calculate structure and organization score.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Structure score
        """
        max_score = self.get_max_score()
        score = 0.0
        
        # Section ordering (40% of structure score)
        order_score = self._score_section_order(resume_data)
        score += order_score * 0.4 * max_score
        
        # Logical flow (30% of structure score)
        flow_score = self._score_logical_flow(resume_data)
        score += flow_score * 0.3 * max_score
        
        # Content organization (30% of structure score)
        organization_score = self._score_content_organization(resume_data)
        score += organization_score * 0.3 * max_score
        
        return self._clamp_score(score)
    
    def _score_section_order(self, resume_data: ResumeData) -> float:
        """
        Score section ordering (0.0 to 1.0).
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Order score
        """
        if not resume_data.sections:
            return 0.0
        
        actual_sections = list(resume_data.sections.keys())
        
        # Score based on how many sections follow recommended order
        matches = 0
        comparisons = 0
        
        for i in range(len(actual_sections) - 1):
            current = actual_sections[i]
            next_section = actual_sections[i + 1]
            
            # Check if both sections are in preferred order
            if current in self.PREFERRED_ORDER and next_section in self.PREFERRED_ORDER:
                current_idx = self.PREFERRED_ORDER.index(current)
                next_idx = self.PREFERRED_ORDER.index(next_section)
                
                # Sections should appear in order
                if current_idx < next_idx:
                    matches += 1
                
                comparisons += 1
        
        if comparisons == 0:
            return 0.5  # Neutral score if can't determine order
        
        return matches / comparisons
    
    def _score_logical_flow(self, resume_data: ResumeData) -> float:
        """
        Score logical flow of resume (0.0 to 1.0).
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Flow score
        """
        score = 0.0
        
        # Contact info should be at top (checked separately)
        if resume_data.contact.email:
            score += 0.3
        
        # Summary should come before details
        if resume_data.has_section('summary'):
            sections = list(resume_data.sections.keys())
            summary_idx = sections.index('summary')
            
            # Summary should be early in resume
            if summary_idx <= 1:
                score += 0.4
            elif summary_idx <= 2:
                score += 0.2
        
        # Experience before education for experienced professionals
        if resume_data.has_section('experience') and resume_data.has_section('education'):
            sections = list(resume_data.sections.keys())
            exp_idx = sections.index('experience')
            edu_idx = sections.index('education')
            
            # For most roles, experience should come before education
            if exp_idx < edu_idx:
                score += 0.3
        
        return min(1.0, score)
    
    def _score_content_organization(self, resume_data: ResumeData) -> float:
        """
        Score content organization within sections (0.0 to 1.0).
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Organization score
        """
        score = 0.0
        checks = 0
        
        # Check experience organization
        if resume_data.has_section('experience'):
            exp_text = resume_data.get_section_text('experience')
            
            # Look for bullet points or dashes (indicates organized content)
            if '•' in exp_text or '-' in exp_text or '*' in exp_text:
                score += 0.4
            
            checks += 1
        
        # Check skills organization
        if resume_data.skills and len(resume_data.skills) >= 3:
            # Having parsed skills indicates organized format
            score += 0.3
            checks += 1
        
        # Check for clear hierarchy (multiple sections)
        if len(resume_data.sections) >= 4:
            score += 0.3
            checks += 1
        
        if checks == 0:
            return 0.5
        
        return min(1.0, score)
    
    def get_category_score(self, resume_data: ResumeData) -> CategoryScore:
        """
        Get category score with details.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            CategoryScore object
        """
        score = self.calculate_score(resume_data)
        
        order_score = self._score_section_order(resume_data)
        flow_score = self._score_logical_flow(resume_data)
        org_score = self._score_content_organization(resume_data)
        
        max_score = self.get_max_score()
        
        breakdown = [
            f"Section Order: {order_score:.1%} ({order_score * 0.4 * max_score:.1f}/{0.4 * max_score:.1f})",
            f"Logical Flow: {flow_score:.1%} ({flow_score * 0.3 * max_score:.1f}/{0.3 * max_score:.1f})",
            f"Organization: {org_score:.1%} ({org_score * 0.3 * max_score:.1f}/{0.3 * max_score:.1f})"
        ]
        
        return CategoryScore(
            category_name="Structure & Organization",
            score=score,
            max_score=max_score,
            details={
                'order_score': order_score,
                'flow_score': flow_score,
                'organization_score': org_score,
                'section_count': len(resume_data.sections)
            },
            breakdown=breakdown
        )
    
    def get_feedback(self, resume_data: ResumeData) -> Dict[str, List[str]]:
        """
        Get feedback on structure and organization.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Feedback dictionary
        """
        strengths = []
        weaknesses = []
        suggestions = []
        
        # Analyze section order
        order_score = self._score_section_order(resume_data)
        if order_score >= 0.8:
            strengths.append("Sections follow logical order")
        elif order_score < 0.5:
            weaknesses.append("Section ordering could be improved")
            suggestions.append(f"Consider this order: {' → '.join([s.title() for s in self.PREFERRED_ORDER])}")
        
        # Analyze flow
        flow_score = self._score_logical_flow(resume_data)
        if flow_score >= 0.7:
            strengths.append("Resume has good logical flow")
        else:
            if resume_data.has_section('summary'):
                sections = list(resume_data.sections.keys())
                if sections.index('summary') > 2:
                    suggestions.append("Move summary section closer to the top of your resume")
            
            if resume_data.has_section('experience') and resume_data.has_section('education'):
                sections = list(resume_data.sections.keys())
                exp_idx = sections.index('experience')
                edu_idx = sections.index('education')
                if exp_idx > edu_idx:
                    suggestions.append("For experienced professionals, list experience before education")
        
        # Analyze organization
        org_score = self._score_content_organization(resume_data)
        if org_score >= 0.7:
            strengths.append("Content is well-organized with clear structure")
        else:
            suggestions.append("Use bullet points to organize your experience and achievements")
            suggestions.append("Ensure clear visual hierarchy with consistent formatting")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions
        }