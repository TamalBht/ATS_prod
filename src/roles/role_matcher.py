"""
Role detection and matching
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from src.roles.role_definitions import RoleManager, RoleDefinition
from src.models.resume_data import ResumeData
from src.config.settings import get_settings
from src.utils.logger import get_logger


@dataclass
class RoleMatch:
    """Represents a role match with confidence."""
    role_id: str
    role_name: str
    confidence: float  # 0.0 to 1.0
    matching_skills: List[str]
    matching_keywords: List[str]
    role_definition: RoleDefinition


class RoleMatcher:
    """Detects and matches resumes to job roles."""
    
    def __init__(self, role_manager: Optional[RoleManager] = None):
        """
        Initialize role matcher.
        
        Args:
            role_manager: RoleManager instance (creates new if None)
        """
        self.logger = get_logger(__name__)
        self.settings = get_settings()
        self.role_manager = role_manager or RoleManager()
        
        self.config = self.settings.get('roles', {})
        self.detection_config = self.config.get('detection', {})
        self.matching_weights = self.config.get('matching_weights', {
            'skills': 0.6,
            'keywords': 0.3,
            'experience': 0.1
        })
    
    def detect_role(self, resume_data: ResumeData) -> Optional[RoleMatch]:
        """
        Detect most likely role for resume.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            RoleMatch with highest confidence, or None if no good match
        """
        matches = self.match_all_roles(resume_data)
        
        if not matches:
            self.logger.info("No role matches found")
            return None
        
        # Get best match
        best_match = matches[0]
        min_confidence = self.detection_config.get('min_confidence', 0.3)
        
        if best_match.confidence < min_confidence:
            self.logger.info(
                f"Best match confidence ({best_match.confidence:.2f}) "
                f"below threshold ({min_confidence})"
            )
            return None
        
        self.logger.info(
            f"Detected role: {best_match.role_name} "
            f"(confidence: {best_match.confidence:.2%})"
        )
        
        return best_match
    
    def match_all_roles(self, resume_data: ResumeData) -> List[RoleMatch]:
        """
        Match resume against all available roles.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            List of RoleMatch objects sorted by confidence (highest first)
        """
        matches = []
        
        for role_id, role_def in self.role_manager.get_all_roles().items():
            confidence = self._calculate_role_confidence(resume_data, role_def)
            
            if confidence > 0:
                # Find matching skills
                resume_skills_lower = [s.lower() for s in resume_data.skills]
                matching_skills = [
                    skill for skill in role_def.get_all_skills()
                    if skill.lower() in resume_skills_lower
                ]
                
                # Find matching keywords
                text_lower = resume_data.raw_text.lower()
                matching_keywords = [
                    kw for kw in role_def.keywords
                    if kw.lower() in text_lower
                ]
                
                match = RoleMatch(
                    role_id=role_id,
                    role_name=role_def.role_name,
                    confidence=confidence,
                    matching_skills=matching_skills,
                    matching_keywords=matching_keywords,
                    role_definition=role_def
                )
                matches.append(match)
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        return matches
    
    def _calculate_role_confidence(
        self,
        resume_data: ResumeData,
        role_def: RoleDefinition
    ) -> float:
        """
        Calculate confidence score for a specific role.
        
        Args:
            resume_data: Parsed resume data
            role_def: Role definition
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        scores = {}
        
        # Skills matching
        if self.detection_config.get('use_skills', True):
            scores['skills'] = self._score_skills_match(resume_data, role_def)
        
        # Keyword matching
        if self.detection_config.get('use_keywords', True):
            scores['keywords'] = self._score_keyword_match(resume_data, role_def)
        
        # Experience matching (placeholder for now)
        if self.detection_config.get('use_experience', True):
            scores['experience'] = self._score_experience_match(resume_data, role_def)
        
        # Calculate weighted confidence
        confidence = 0.0
        total_weight = 0.0
        
        for component, score in scores.items():
            weight = self.matching_weights.get(component, 0.0)
            confidence += score * weight
            total_weight += weight
        
        if total_weight > 0:
            confidence /= total_weight
        
        return confidence
    
    def _score_skills_match(
        self,
        resume_data: ResumeData,
        role_def: RoleDefinition
    ) -> float:
        """
        Score skills match (0.0 to 1.0).
        
        Args:
            resume_data: Parsed resume data
            role_def: Role definition
            
        Returns:
            Skills match score
        """
        if not resume_data.skills:
            return 0.0
        
        resume_skills_lower = set(s.lower() for s in resume_data.skills)
        
        # Check core skills (weight: 60%)
        core_skills = [s.lower() for s in role_def.skills.core]
        core_matches = sum(1 for skill in core_skills if skill in resume_skills_lower)
        core_score = core_matches / len(core_skills) if core_skills else 0
        
        # Check important skills (weight: 30%)
        important_skills = [s.lower() for s in role_def.skills.important]
        important_matches = sum(1 for skill in important_skills if skill in resume_skills_lower)
        important_score = important_matches / len(important_skills) if important_skills else 0
        
        # Check bonus skills (weight: 10%)
        bonus_skills = [s.lower() for s in role_def.skills.bonus]
        bonus_matches = sum(1 for skill in bonus_skills if skill in resume_skills_lower)
        bonus_score = bonus_matches / len(bonus_skills) if bonus_skills else 0
        
        # Weighted average
        total_score = (core_score * 0.6 + important_score * 0.3 + bonus_score * 0.1)
        
        return total_score
    
    def _score_keyword_match(
        self,
        resume_data: ResumeData,
        role_def: RoleDefinition
    ) -> float:
        """
        Score keyword match (0.0 to 1.0).
        
        Args:
            resume_data: Parsed resume data
            role_def: Role definition
            
        Returns:
            Keyword match score
        """
        if not role_def.keywords:
            return 0.5  # Neutral if no keywords defined
        
        text_lower = resume_data.raw_text.lower()
        
        matches = sum(1 for kw in role_def.keywords if kw.lower() in text_lower)
        score = matches / len(role_def.keywords)
        
        return score
    
    def _score_experience_match(
        self,
        resume_data: ResumeData,
        role_def: RoleDefinition
    ) -> float:
        """
        Score experience match (0.0 to 1.0).
        
        Placeholder for now - could extract years of experience in Phase 4+.
        
        Args:
            resume_data: Parsed resume data
            role_def: Role definition
            
        Returns:
            Experience match score
        """
        # For now, just check if experience section exists
        if resume_data.has_section('experience'):
            return 0.7
        return 0.3