"""
Section completeness scoring
"""

from typing import Dict, List, Tuple

from src.scoring.base_scorer import BaseScorer
from src.models.resume_data import ResumeData
from src.models.score_data import SectionScore, CategoryScore


class SectionScorer(BaseScorer):
    """Scores resume based on section completeness."""
    
    REQUIRED_SECTIONS = ['summary', 'experience', 'education', 'skills']
    OPTIONAL_SECTIONS = ['projects', 'certifications']
    
    def get_max_score(self) -> float:
        """Get maximum section completeness score."""
        return self.config.get('max_scores', {}).get('section_completeness', 40)
    
    def calculate_score(self, resume_data: ResumeData) -> float:
        """
        Calculate section completeness score.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Section completeness score
        """
        score = 0.0
        max_score = self.get_max_score()
        section_weights = self.config.get('section_weights', {})
        
        # Score each section
        for section_name, weight in section_weights.items():
            section_score = self._score_section(resume_data, section_name)
            weighted_score = section_score * weight * max_score
            score += weighted_score
            
            self.logger.debug(
                f"Section '{section_name}': {section_score:.2f} * {weight} * {max_score} = {weighted_score:.2f}"
            )
        
        return self._clamp_score(score)
    
    def _score_section(self, resume_data: ResumeData, section_name: str) -> float:
        """
        Score an individual section (0.0 to 1.0).
        
        Args:
            resume_data: Parsed resume data
            section_name: Name of section to score
            
        Returns:
            Section score (0.0 to 1.0)
        """
        # Check if section exists
        if not resume_data.has_section(section_name):
            return 0.0
        
        section_content = resume_data.get_section_text(section_name)
        if not section_content:
            return 0.0
        
        # Start with full score for presence
        score = 1.0
        
        # Check minimum length requirement
        min_lengths = self.config.get('min_content_length', {})
        min_length = min_lengths.get(section_name, 50)
        
        content_length = len(section_content)
        
        if content_length < min_length:
            # Penalize for being too short
            penalty = 0.5 * (1 - content_length / min_length)
            score -= penalty
            self.logger.debug(
                f"Section '{section_name}' too short ({content_length} < {min_length}): penalty {penalty:.2f}"
            )
        
        return max(0.0, score)
    
    def get_section_scores(self, resume_data: ResumeData) -> Dict[str, SectionScore]:
        """
        Get detailed scores for each section.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Dictionary of section scores
        """
        section_scores = {}
        section_weights = self.config.get('section_weights', {})
        max_score = self.get_max_score()
        
        for section_name in section_weights.keys():
            present = resume_data.has_section(section_name)
            content = resume_data.get_section_text(section_name) if present else ""
            content_length = len(content) if content else 0
            
            # Calculate score
            raw_score = self._score_section(resume_data, section_name)
            weight = section_weights[section_name]
            weighted_score = raw_score * weight * max_score
            
            # Identify issues
            issues = []
            suggestions = []
            
            if not present:
                issues.append(f"Section missing")
                suggestions.append(f"Add a {section_name} section to your resume")
            else:
                min_length = self.config.get('min_content_length', {}).get(section_name, 50)
                if content_length < min_length:
                    issues.append(f"Content too short ({content_length} chars, minimum {min_length})")
                    suggestions.append(f"Expand your {section_name} section with more details")
            
            section_scores[section_name] = SectionScore(
                section_name=section_name,
                score=weighted_score,
                max_score=weight * max_score,
                present=present,
                content_length=content_length,
                issues=issues,
                suggestions=suggestions
            )
        
        return section_scores
    
    def get_category_score(self, resume_data: ResumeData) -> CategoryScore:
        """
        Get category score with details.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            CategoryScore object
        """
        score = self.calculate_score(resume_data)
        section_scores = self.get_section_scores(resume_data)
        
        # Build breakdown
        breakdown = []
        for section_name, section_score in section_scores.items():
            breakdown.append(
                f"{section_name.title()}: {section_score.score:.1f}/{section_score.max_score:.1f}"
            )
        
        # Count present sections
        present_count = sum(1 for s in section_scores.values() if s.present)
        total_count = len(section_scores)
        
        return CategoryScore(
            category_name="Section Completeness",
            score=score,
            max_score=self.get_max_score(),
            details={
                'sections_present': present_count,
                'total_sections': total_count,
                'section_scores': {k: v.score for k, v in section_scores.items()}
            },
            breakdown=breakdown
        )
    
    def get_feedback(self, resume_data: ResumeData) -> Dict[str, List[str]]:
        """
        Get feedback on section completeness.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Feedback dictionary
        """
        strengths = []
        weaknesses = []
        suggestions = []
        
        section_scores = self.get_section_scores(resume_data)
        
        # Identify strengths
        for section_name, section_score in section_scores.items():
            if section_score.present and section_score.score >= section_score.max_score * 0.9:
                strengths.append(f"Strong {section_name} section with adequate detail")
        
        # Identify weaknesses and suggestions
        for section_name, section_score in section_scores.items():
            if not section_score.present:
                if section_name in self.REQUIRED_SECTIONS:
                    weaknesses.append(f"Missing required section: {section_name}")
                    suggestions.append(f"Add a {section_name} section - this is expected by ATS systems")
                else:
                    suggestions.append(f"Consider adding a {section_name} section to strengthen your resume")
            elif section_score.issues:
                for issue in section_score.issues:
                    weaknesses.append(f"{section_name.title()}: {issue}")
                for suggestion in section_score.suggestions:
                    suggestions.append(suggestion)
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions
        }