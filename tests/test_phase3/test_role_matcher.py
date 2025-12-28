"""
Unit tests for role matcher
"""

import pytest
from src.roles.role_matcher import RoleMatcher
from src.roles.role_definitions import RoleManager, RoleDefinition, RoleSkills
from src.models.resume_data import ResumeData, ResumeMetadata


@pytest.fixture
def mock_role_manager():
    """Create mock role manager with test roles."""
    manager = RoleManager(roles_dir=None)  # Don't load from files
    
    # Create test backend role
    backend = RoleDefinition(
        role_id='backend',
        role_name='Backend Engineer',
        section_weights={'experience': 0.35, 'skills': 0.25},
        skills=RoleSkills(
            core=['Python', 'SQL', 'REST API'],
            important=['Docker', 'Redis'],
            bonus=['Kubernetes']
        ),
        keywords=['backend', 'API', 'server']
    )
    
    # Create test frontend role
    frontend = RoleDefinition(
        role_id='frontend',
        role_name='Frontend Engineer',
        section_weights={'experience': 0.32, 'skills': 0.28},
        skills=RoleSkills(
            core=['JavaScript', 'React', 'CSS'],
            important=['TypeScript', 'Redux'],
            bonus=['Next.js']
        ),
        keywords=['frontend', 'UI', 'React']
    )
    
    manager.roles = {'backend': backend, 'frontend': frontend}
    return manager


class TestRoleMatcher:
    """Test role matcher functionality."""
    
    def test_matcher_initialization(self, mock_role_manager):
        """Test matcher initializes correctly."""
        matcher = RoleMatcher(mock_role_manager)
        assert matcher.role_manager is not None
    
    def test_detect_backend_role(self, mock_role_manager):
        """Test detection of backend role."""
        matcher = RoleMatcher(mock_role_manager)
        
        resume = ResumeData()
        resume.skills = ['Python', 'SQL', 'REST API', 'Docker']
        resume.raw_text = 'Backend engineer with API development experience'
        resume.metadata = ResumeMetadata(
            file_path='test.pdf',
            file_name='test.pdf',
            file_size=1000,
            file_type='.pdf',
            parsed_at='2024-01-01',
            parsing_time_ms=100
        )
        
        role_match = matcher.detect_role(resume)
        
        assert role_match is not None
        assert role_match.role_id == 'backend'
        assert role_match.confidence > 0
    
    def test_detect_frontend_role(self, mock_role_manager):
        """Test detection of frontend role."""
        matcher = RoleMatcher(mock_role_manager)
        
        resume = ResumeData()
        resume.skills = ['JavaScript', 'React', 'CSS', 'TypeScript']
        resume.raw_text = 'Frontend developer specializing in React UI development'
        resume.metadata = ResumeMetadata(
            file_path='test.pdf',
            file_name='test.pdf',
            file_size=1000,
            file_type='.pdf',
            parsed_at='2024-01-01',
            parsing_time_ms=100
        )
        
        role_match = matcher.detect_role(resume)
        
        assert role_match is not None
        assert role_match.role_id == 'frontend'
    
    def test_no_role_match(self, mock_role_manager):
        """Test when no role matches well."""
        matcher = RoleMatcher(mock_role_manager)
        
        resume = ResumeData()
        resume.skills = ['Excel', 'PowerPoint']
        resume.raw_text = 'Business analyst'
        resume.metadata = ResumeMetadata(
            file_path='test.pdf',
            file_name='test.pdf',
            file_size=1000,
            file_type='.pdf',
            parsed_at='2024-01-01',
            parsing_time_ms=100
        )
        
        role_match = matcher.detect_role(resume)
        
        # Should return None or low confidence match
        assert role_match is None or role_match.confidence < 0.5
    
    def test_match_all_roles(self, mock_role_manager):
        """Test matching against all roles."""
        matcher = RoleMatcher(mock_role_manager)
        
        resume = ResumeData()
        resume.skills = ['Python', 'JavaScript', 'SQL']
        resume.raw_text = 'Full stack developer'
        resume.metadata = ResumeMetadata(
            file_path='test.pdf',
            file_name='test.pdf',
            file_size=1000,
            file_type='.pdf',
            parsed_at='2024-01-01',
            parsing_time_ms=100
        )
        
        matches = matcher.match_all_roles(resume)
        
        assert len(matches) > 0
        # Should be sorted by confidence
        for i in range(len(matches) - 1):
            assert matches[i].confidence >= matches[i + 1].confidence