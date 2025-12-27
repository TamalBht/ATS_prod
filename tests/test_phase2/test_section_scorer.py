"""
Unit tests for section scorer
"""

import pytest
from src.scoring.section_scorer import SectionScorer
from src.models.resume_data import ResumeData, Section


class TestSectionScorer:
    """Test section scoring functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.scorer = SectionScorer()
    
    def test_scorer_initialization(self):
        """Test scorer initializes correctly."""
        assert self.scorer is not None
        assert self.scorer.get_max_score() > 0
    
    def test_score_complete_resume(self):
        """Test scoring of complete resume."""
        resume = ResumeData()
        resume.sections = {
            'summary': Section('summary', 'A' * 150, 1.0),
            'experience': Section('experience', 'B' * 250, 1.0),
            'education': Section('education', 'C' * 100, 1.0),
            'skills': Section('skills', 'D' * 80, 1.0),
            'projects': Section('projects', 'E' * 150, 1.0)
        }
        
        score = self.scorer.calculate_score(resume)
        
        assert score > 0
        assert score <= self.scorer.get_max_score()
    
    def test_score_missing_sections(self):
        """Test scoring with missing sections."""
        resume = ResumeData()
        resume.sections = {
            'summary': Section('summary', 'A' * 150, 1.0)
        }
        
        score = self.scorer.calculate_score(resume)
        
        # Should be penalized for missing sections
        assert score < self.scorer.get_max_score() / 2
    
    def test_score_short_content(self):
        """Test scoring with short content."""
        resume = ResumeData()
        resume.sections = {
            'summary': Section('summary', 'Too short', 1.0),
            'experience': Section('experience', 'Also short', 1.0)
        }
        
        score = self.scorer.calculate_score(resume)
        
        # Should be penalized for short content
        assert score < self.scorer.get_max_score() / 3
    
    def test_get_section_scores(self):
        """Test getting detailed section scores."""
        resume = ResumeData()
        resume.sections = {
            'summary': Section('summary', 'A' * 150, 1.0),
            'skills': Section('skills', 'B' * 80, 1.0)
        }
        
        section_scores = self.scorer.get_section_scores(resume)
        
        assert 'summary' in section_scores
        assert 'skills' in section_scores
        assert section_scores['summary'].present is True
        assert section_scores['experience'].present is False
    
    def test_category_score(self):
        """Test getting category score."""
        resume = ResumeData()
        resume.sections = {
            'summary': Section('summary', 'A' * 150, 1.0),
            'experience': Section('experience', 'B' * 250, 1.0),
            'education': Section('education', 'C' * 100, 1.0),
            'skills': Section('skills', 'D' * 80, 1.0)
        }
        
        category = self.scorer.get_category_score(resume)
        
        assert category.category_name == "Section Completeness"
        assert category.score > 0
        assert category.max_score == self.scorer.get_max_score()
        assert 'sections_present' in category.details
    
    def test_feedback_generation(self):
        """Test feedback generation."""
        resume = ResumeData()
        resume.sections = {
            'summary': Section('summary', 'A' * 150, 1.0)
        }
        
        feedback = self.scorer.get_feedback(resume)
        
        assert 'strengths' in feedback
        assert 'weaknesses' in feedback
        assert 'suggestions' in feedback
        assert len(feedback['weaknesses']) > 0  # Missing required sections