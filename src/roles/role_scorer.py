"""
Role-aware scoring enhancements
"""

from typing import Dict, List, Tuple

from src.roles.role_definitions import RoleDefinition
from src.models.resume_data import ResumeData
from src.utils.logger import get_logger


class RoleScorer:
    """Provides role-specific scoring enhancements."""
    
    def __init__(self):
        """Initialize role scorer."""
        self.logger = get_logger(__name__)
    
    def get_role_section_weights(self, role_def: RoleDefinition) -> Dict[str, float]:
        """
        Get section weights for a specific role.
        
        Args:
            role_def: Role definition
            
        Returns:
            Dictionary of section weights
        """
        # Start with role's defined weights
        weights = role_def.section_weights.copy()
        
        # Ensure all standard sections have weights
        standard_sections = {
            'summary': 0.15,
            'experience': 0.30,
            'education': 0.20,
            'skills': 0.20,
            'projects': 0.10,
            'certifications': 0.05
        }
        
        for section, default_weight in standard_sections.items():
            if section not in weights:
                weights[section] = default_weight
        
        # Normalize to sum to 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def analyze_skill_gaps(
        self,
        resume_data: ResumeData,
        role_def: RoleDefinition
    ) -> Dict[str, List[str]]:
        """
        Analyze skill gaps for a role.
        
        Args:
            resume_data: Parsed resume data
            role_def: Role definition
            
        Returns:
            Dictionary with 'missing_core', 'missing_important', 'present' skills
        """
        resume_skills_lower = set(s.lower() for s in resume_data.skills)
        
        # Find missing core skills
        missing_core = [
            skill for skill in role_def.skills.core
            if skill.lower() not in resume_skills_lower
        ]
        
        # Find missing important skills
        missing_important = [
            skill for skill in role_def.skills.important
            if skill.lower() not in resume_skills_lower
        ]
        
        # Find present skills from role definition
        all_role_skills = role_def.get_all_skills()
        present = [
            skill for skill in all_role_skills
            if skill.lower() in resume_skills_lower
        ]
        
        return {
            'missing_core': missing_core,
            'missing_important': missing_important,
            'present': present
        }
    
    def calculate_skill_coverage(
        self,
        resume_data: ResumeData,
        role_def: RoleDefinition
    ) -> Dict[str, float]:
        """
        Calculate skill coverage percentages.
        
        Args:
            resume_data: Parsed resume data
            role_def: Role definition
            
        Returns:
            Dictionary with coverage percentages
        """
        resume_skills_lower = set(s.lower() for s in resume_data.skills)
        
        # Core skill coverage
        core_skills = [s.lower() for s in role_def.skills.core]
        core_coverage = (
            sum(1 for s in core_skills if s in resume_skills_lower) / len(core_skills)
            if core_skills else 0.0
        )
        
        # Important skill coverage
        important_skills = [s.lower() for s in role_def.skills.important]
        important_coverage = (
            sum(1 for s in important_skills if s in resume_skills_lower) / len(important_skills)
            if important_skills else 0.0
        )
        
        # Bonus skill coverage
        bonus_skills = [s.lower() for s in role_def.skills.bonus]
        bonus_coverage = (
            sum(1 for s in bonus_skills if s in resume_skills_lower) / len(bonus_skills)
            if bonus_skills else 0.0
        )
        
        # Overall coverage (weighted)
        overall_coverage = (
            core_coverage * 0.6 +
            important_coverage * 0.3 +
            bonus_coverage * 0.1
        )
        
        return {
            'core': core_coverage,
            'important': important_coverage,
            'bonus': bonus_coverage,
            'overall': overall_coverage
        }
    
    def generate_role_feedback(
        self,
        resume_data: ResumeData,
        role_def: RoleDefinition
    ) -> Dict[str, List[str]]:
        """
        Generate role-specific feedback.
        
        Args:
            resume_data: Parsed resume data
            role_def: Role definition
            
        Returns:
            Dictionary with strengths, weaknesses, suggestions
        """
        strengths = []
        weaknesses = []
        suggestions = []
        
        # Analyze skill gaps
        skill_gaps = self.analyze_skill_gaps(resume_data, role_def)
        skill_coverage = self.calculate_skill_coverage(resume_data, role_def)
        
        # Strengths
        if skill_coverage['core'] >= 0.7:
            strengths.append(
                f"Strong core skill set for {role_def.role_name} role "
                f"({skill_coverage['core']:.0%} coverage)"
            )
        
        if skill_coverage['bonus'] >= 0.3:
            strengths.append(
                f"Good bonus skills for {role_def.role_name} "
                f"({len(skill_gaps['present'])} relevant skills)"
            )
        
        # Weaknesses and suggestions
        if skill_gaps['missing_core']:
            weaknesses.append(
                f"Missing core {role_def.role_name} skills: "
                f"{', '.join(skill_gaps['missing_core'][:3])}"
                + (" and more" if len(skill_gaps['missing_core']) > 3 else "")
            )
            
            # Suggest top 3 missing core skills
            top_missing = skill_gaps['missing_core'][:3]
            for skill in top_missing:
                suggestions.append(
                    f"Add '{skill}' to your skills - it's a core requirement for {role_def.role_name}"
                )
        
        if skill_coverage['important'] < 0.5 and skill_gaps['missing_important']:
            top_important = skill_gaps['missing_important'][:2]
            suggestions.append(
                f"Consider adding important skills: {', '.join(top_important)}"
            )
        
        # Section-specific feedback
        role_weights = role_def.section_weights
        if 'skills' in role_weights and role_weights['skills'] > 0.25:
            if not resume_data.skills or len(resume_data.skills) < 10:
                suggestions.append(
                    f"For {role_def.role_name} roles, list at least 10-15 relevant technical skills"
                )
        
        if 'projects' in role_weights and role_weights['projects'] > 0.08:
            if not resume_data.has_section('projects'):
                suggestions.append(
                    f"Add a projects section - important for {role_def.role_name} roles"
                )
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions
        }
    
    def get_skill_match_score(
        self,
        resume_data: ResumeData,
        role_def: RoleDefinition
    ) -> float:
        """
        Calculate skill match score for role (0-100).
        
        Args:
            resume_data: Parsed resume data
            role_def: Role definition
            
        Returns:
            Skill match score
        """
        coverage = self.calculate_skill_coverage(resume_data, role_def)
        
        # Convert overall coverage to score out of 100
        return coverage['overall'] * 100