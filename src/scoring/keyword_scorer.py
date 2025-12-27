"""
Keyword presence and content quality scoring
"""

import re
from typing import Dict, List, Set

from src.scoring.base_scorer import BaseScorer
from src.models.resume_data import ResumeData
from src.models.score_data import CategoryScore


class KeywordScorer(BaseScorer):
    """Scores resume based on keyword presence and content quality."""
    
    def get_max_score(self) -> float:
        """Get maximum content quality score."""
        return self.config.get('max_scores', {}).get('content_quality', 30)
    
    def calculate_score(self, resume_data: ResumeData) -> float:
        """
        Calculate content quality score based on keywords.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Content quality score
        """
        max_score = self.get_max_score()
        score = 0.0
        
        # Keyword presence scoring (60% of content quality)
        keyword_score = self._score_keywords(resume_data)
        score += keyword_score * 0.6 * max_score
        
        # Quantifiable achievements (20% of content quality)
        achievement_score = self._score_achievements(resume_data)
        score += achievement_score * 0.2 * max_score
        
        # Content richness (20% of content quality)
        richness_score = self._score_content_richness(resume_data)
        score += richness_score * 0.2 * max_score
        
        return self._clamp_score(score)
    
    def _score_keywords(self, resume_data: ResumeData) -> float:
        """
        Score based on essential keyword presence (0.0 to 1.0).
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Keyword score
        """
        text = resume_data.raw_text.lower()
        
        essential_keywords = self.config.get('essential_keywords', {})
        found_categories = 0
        total_categories = len(essential_keywords)
        
        for category, keywords in essential_keywords.items():
            # Check if any keyword from this category is present
            if any(keyword.lower() in text for keyword in keywords):
                found_categories += 1
                self.logger.debug(f"Found keywords from category: {category}")
        
        if total_categories == 0:
            return 1.0
        
        return found_categories / total_categories
    
    def _score_achievements(self, resume_data: ResumeData) -> float:
        """
        Score based on quantifiable achievements (0.0 to 1.0).
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Achievement score
        """
        # Look for numbers/percentages in experience section
        experience_text = resume_data.get_section_text('experience') or ""
        
        if not experience_text:
            return 0.0
        
        # Patterns indicating quantifiable achievements
        number_patterns = [
            r'\d+%',  # Percentages (e.g., "40%")
            r'\$\d+',  # Dollar amounts
            r'\d+\+',  # Numbers with plus (e.g., "5+")
            r'\d+[KMB]',  # Thousands/Millions/Billions (e.g., "1M")
        ]
        
        achievement_count = 0
        for pattern in number_patterns:
            matches = re.findall(pattern, experience_text)
            achievement_count += len(matches)
        
        # Score based on number of quantifiable achievements
        # 5+ achievements = full score
        return min(1.0, achievement_count / 5.0)
    
    def _score_content_richness(self, resume_data: ResumeData) -> float:
        """
        Score based on overall content richness (0.0 to 1.0).
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Richness score
        """
        score = 0.0
        
        # Variety of sections (up to 0.4)
        section_count = len(resume_data.sections)
        score += min(0.4, section_count / 6.0 * 0.4)
        
        # Skills variety (up to 0.3)
        skills_count = len(resume_data.skills)
        score += min(0.3, skills_count / 15.0 * 0.3)
        
        # Content depth - total words (up to 0.3)
        total_words = resume_data.metadata.total_words if resume_data.metadata else 0
        # Target: 500+ words for full score
        score += min(0.3, total_words / 500.0 * 0.3)
        
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
        
        # Calculate component scores
        keyword_score = self._score_keywords(resume_data)
        achievement_score = self._score_achievements(resume_data)
        richness_score = self._score_content_richness(resume_data)
        
        max_score = self.get_max_score()
        
        breakdown = [
            f"Keywords: {keyword_score:.1%} ({keyword_score * 0.6 * max_score:.1f}/{0.6 * max_score:.1f})",
            f"Achievements: {achievement_score:.1%} ({achievement_score * 0.2 * max_score:.1f}/{0.2 * max_score:.1f})",
            f"Content Richness: {richness_score:.1%} ({richness_score * 0.2 * max_score:.1f}/{0.2 * max_score:.1f})"
        ]
        
        return CategoryScore(
            category_name="Content Quality",
            score=score,
            max_score=max_score,
            details={
                'keyword_score': keyword_score,
                'achievement_score': achievement_score,
                'richness_score': richness_score
            },
            breakdown=breakdown
        )
    
    def get_feedback(self, resume_data: ResumeData) -> Dict[str, List[str]]:
        """
        Get feedback on content quality.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Feedback dictionary
        """
        strengths = []
        weaknesses = []
        suggestions = []
        
        # Keyword analysis
        keyword_score = self._score_keywords(resume_data)
        if keyword_score >= 0.8:
            strengths.append("Good coverage of essential keywords")
        elif keyword_score < 0.5:
            weaknesses.append("Limited use of industry-standard keywords")
            suggestions.append("Include more technical terms and action verbs relevant to your field")
        
        # Achievement analysis
        achievement_score = self._score_achievements(resume_data)
        if achievement_score >= 0.6:
            strengths.append("Resume includes quantifiable achievements")
        else:
            weaknesses.append("Few quantifiable achievements or metrics")
            suggestions.append("Add specific numbers, percentages, or metrics to demonstrate impact")
            suggestions.append("Example: 'Improved performance by 40%' instead of 'Improved performance'")
        
        # Content richness
        richness_score = self._score_content_richness(resume_data)
        if richness_score >= 0.7:
            strengths.append("Comprehensive content with good variety")
        else:
            if len(resume_data.skills) < 10:
                suggestions.append("List more relevant skills to demonstrate breadth of expertise")
            if resume_data.metadata and resume_data.metadata.total_words < 300:
                suggestions.append("Expand your experience descriptions with more detail")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions
        }