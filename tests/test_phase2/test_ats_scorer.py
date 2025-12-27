"""
Unit tests for ATS scorer
"""

import pytest
from src.scoring.ats_scorer import ATSScorer
from src.models.resume_data import ResumeData, Section, ContactInfo, ResumeMetadata


@pytest.fixture
def complete_resume():
    """Create a complete sample resume."""
    resume = ResumeData()
    
    resume.contact = ContactInfo(
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        linkedin="linkedin.com/in/johndoe",
        github="github.com/johndoe"
    )
    
    resume.sections = {
        'summary': Section('summary', 'Software Engineer with 5+ years of experience building scalable applications', 1.0),
        'experience': Section('experience', 'Led development of platform serving 1M+ users. Improved performance by 40%.', 1.0),
        'education': Section('education', 'BS in Computer Science from University', 1.0),
        'skills': Section('skills', 'Python, JavaScript, React, Django, PostgreSQL', 1.0),
        'projects': Section('projects', 'Built e-commerce platform using React and Django', 1.0)
    }
    
    resume.skills = ['Python', 'JavaScript', 'React', 'Django', 'PostgreSQL']
    resume.raw_text = ' '.join([s.content for s in resume.sections.values()])
    
    resume.metadata = ResumeMetadata(
        file_path='test.pdf',
        file_name='test.pdf',
        file_size=1000,
        file_type='.pdf',
        parsed_at='2024-01-01',
        parsing_time_ms=100,
        total_words=50
    )
    
    return resume


class TestATSScorer:
    """Test ATS scorer functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.scorer = ATSScorer()
    
    def test_scorer_initialization(self):
        """Test scorer initializes with all components."""
        assert self.scorer.section_scorer is not None
        assert self.scorer.keyword_scorer is not None
        assert self.scorer.contact_scorer is not None
        assert self.scorer.structure_scorer is not None
    
    def test_score_complete_resume(self, complete_resume):
        """Test scoring a complete resume."""
        score = self.scorer.score(complete_resume)
        
        assert score is not None
        assert score.total_score > 0
        assert score.total_score <= 100
        assert score.grade in ['A', 'B', 'C', 'D', 'F']
    
    def test_score_has_all_categories(self, complete_resume):
        """Test that score includes all categories."""
        score = self.scorer.score(complete_resume)
        
        assert score.section_completeness is not None
        assert score.content_quality is not None
        assert score.contact_information is not None
        assert score.structure_organization is not None
    
    def test_score_has_feedback(self, complete_resume):
        """Test that score includes feedback."""
        score = self.scorer.score(complete_resume)
        
        assert len(score.strengths) > 0 or len(score.weaknesses) > 0
        assert len(score.suggestions) >= 0
    
    def test_score_empty_resume(self):
        """Test scoring an empty resume."""
        resume = ResumeData()
        score = self.scorer.score(resume)
        
        # Should have low score but not crash
        assert score.total_score < 50
        assert len(score.weaknesses) > 0
    
    def test_score_minimal_resume(self):
        """Test scoring resume with minimal info."""
        resume = ResumeData()
        resume.contact = ContactInfo(email="test@example.com")
        resume.sections = {
            'summary': Section('summary', 'Engineer', 1.0)
        }
        
        score = self.scorer.score(resume)
        
        assert score.total_score > 0
        assert score.total_score < 50
    
    def test_score_to_dict(self, complete_resume):
        """Test score serialization to dict."""
        score = self.scorer.score(complete_resume)
        score_dict = score.to_dict()
        
        assert isinstance(score_dict, dict)
        assert 'total_score' in score_dict
        assert 'percentage' in score_dict
        assert 'grade' in score_dict
        assert 'categories' in score_dict
        assert 'feedback' in score_dict
    
    def test_score_metadata(self, complete_resume):
        """Test that scoring metadata is included."""
        score = self.scorer.score(complete_resume)
        
        assert score.scoring_metadata is not None
        assert 'scored_at' in score.scoring_metadata
        assert 'scoring_time_ms' in score.scoring_metadata
    
    def test_score_percentage_calculation(self, complete_resume):
        """Test percentage calculation."""
        score = self.scorer.score(complete_resume)
        
        expected_percentage = (score.total_score / score.max_score) * 100
        assert abs(score.percentage - expected_percentage) < 0.01
    
    def test_grade_assignment(self):
        """Test grade assignment based on score."""
        resume = ResumeData()
        resume.contact = ContactInfo(
            email="test@example.com",
            phone="555-1234",
            linkedin="linkedin.com/in/test"
        )
        resume.sections = {
            'summary': Section('summary', 'A' * 150, 1.0),
            'experience': Section('experience', 'Led development of software serving 1M users. Improved by 50%. Built platform. Managed 5+ engineers.', 1.0),
            'education': Section('education', 'BS Computer Science', 1.0),
            'skills': Section('skills', 'Python, Java, React, Node, SQL, Docker, AWS, Git, Agile', 1.0),
            'projects': Section('projects', 'Built complex application', 1.0)
        }
        resume.skills = ['Python', 'Java', 'React', 'Node', 'SQL']
        resume.raw_text = 'software engineer developer led developed managed built experience years'
        resume.metadata = ResumeMetadata(
            file_path='test.pdf',
            file_name='test.pdf',
            file_size=1000,
            file_type='.pdf',
            parsed_at='2024-01-01',
            parsing_time_ms=100,
            total_words=500
        )
        
        score = self.scorer.score(resume)
        
        # High score should get good grade
        if score.percentage >= 90:
            assert score.grade == 'A'
        elif score.percentage >= 80:
            assert score.grade in ['A', 'B']