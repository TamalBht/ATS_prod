"""
Main ATS scorer orchestrator
"""

import time
from datetime import datetime
from typing import Dict, Any

from src.scoring.base_scorer import BaseScorer
from src.scoring.section_scorer import SectionScorer
from src.scoring.keyword_scorer import KeywordScorer
from src.scoring.contact_scorer import ContactScorer
from src.scoring.structure_scorer import StructureScorer
from src.models.resume_data import ResumeData
from src.models.score_data import ATSScore
from src.utils.logger import get_logger


class ATSScorer:
    """Main orchestrator for ATS scoring."""
    
    def __init__(self):
        """Initialize ATS scorer with all component scorers."""
        self.logger = get_logger(__name__)
        
        # Initialize component scorers
        self.section_scorer = SectionScorer()
        self.keyword_scorer = KeywordScorer()
        self.contact_scorer = ContactScorer()
        self.structure_scorer = StructureScorer()
    
    def score(self, resume_data: ResumeData) -> ATSScore:
        """
        Calculate complete ATS score for resume.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            ATSScore object with complete scoring results
        """
        start_time = time.time()
        self.logger.info("Starting ATS scoring")
        
        # Calculate category scores
        section_category = self.section_scorer.get_category_score(resume_data)
        keyword_category = self.keyword_scorer.get_category_score(resume_data)
        contact_category = self.contact_scorer.get_category_score(resume_data)
        structure_category = self.structure_scorer.get_category_score(resume_data)
        
        # Calculate total score
        total_score = (
            section_category.score +
            keyword_category.score +
            contact_category.score +
            structure_category.score
        )
        
        # Create ATS score object
        ats_score = ATSScore(
            total_score=total_score,
            section_completeness=section_category,
            content_quality=keyword_category,
            contact_information=contact_category,
            structure_organization=structure_category,
            section_scores=self.section_scorer.get_section_scores(resume_data)
        )
        
        # Collect feedback from all scorers
        self._collect_feedback(ats_score, resume_data)
        
        # Add metadata
        scoring_time = (time.time() - start_time) * 1000  # ms
        ats_score.scoring_metadata = {
            'scored_at': datetime.now().isoformat(),
            'scoring_time_ms': scoring_time,
            'scorer_version': '2.0.0',
            'resume_file': resume_data.metadata.file_name if resume_data.metadata else 'unknown'
        }
        
        self.logger.info(
            f"ATS scoring complete: {total_score:.2f}/100 "
            f"(Grade: {ats_score.grade}) in {scoring_time:.2f}ms"
        )
        
        return ats_score
    
    def _collect_feedback(self, ats_score: ATSScore, resume_data: ResumeData) -> None:
        """
        Collect feedback from all scorers.
        
        Args:
            ats_score: ATSScore object to populate
            resume_data: Parsed resume data
        """
        # Collect from all scorers
        scorers = [
            self.section_scorer,
            self.keyword_scorer,
            self.contact_scorer,
            self.structure_scorer
        ]
        
        for scorer in scorers:
            feedback = scorer.get_feedback(resume_data)
            
            for strength in feedback.get('strengths', []):
                ats_score.add_strength(strength)
            
            for weakness in feedback.get('weaknesses', []):
                ats_score.add_weakness(weakness)
            
            for suggestion in feedback.get('suggestions', []):
                ats_score.add_suggestion(suggestion)
        
        # Add overall feedback based on total score
        self._add_overall_feedback(ats_score)
    
    def _add_overall_feedback(self, ats_score: ATSScore) -> None:
        """
        Add overall feedback based on total score.
        
        Args:
            ats_score: ATSScore object to populate
        """
        percentage = ats_score.percentage
        
        if percentage >= 90:
            ats_score.add_strength("Excellent ATS-optimized resume")
            ats_score.add_strength("Strong likelihood of passing automated screening")
        elif percentage >= 80:
            ats_score.add_strength("Well-optimized resume with good ATS compatibility")
        elif percentage >= 70:
            ats_score.add_suggestion("Good foundation - addressing key weaknesses will significantly improve ATS compatibility")
        elif percentage >= 60:
            ats_score.add_weakness("Resume needs improvement to pass most ATS systems")
            ats_score.add_suggestion("Focus on adding missing sections and essential keywords")
        else:
            ats_score.add_weakness("Resume may struggle with ATS screening")
            ats_score.add_suggestion("Significant improvements needed - start with section completeness")
        
        # Category-specific guidance
        if ats_score.section_completeness and ats_score.section_completeness.percentage < 70:
            ats_score.add_suggestion("Priority: Improve section completeness (currently {:.0f}%)".format(
                ats_score.section_completeness.percentage
            ))
        
        if ats_score.contact_information and ats_score.contact_information.percentage < 70:
            ats_score.add_suggestion("Priority: Complete contact information (currently {:.0f}%)".format(
                ats_score.contact_information.percentage
            ))
            """
Main ATS scorer orchestrator with role-aware support
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional

from src.scoring.base_scorer import BaseScorer
from src.scoring.section_scorer import SectionScorer
from src.scoring.keyword_scorer import KeywordScorer
from src.scoring.contact_scorer import ContactScorer
from src.scoring.structure_scorer import StructureScorer
from src.models.resume_data import ResumeData
from src.models.score_data import ATSScore
from src.utils.logger import get_logger

# Role-aware imports (optional)
try:
    from src.roles.role_matcher import RoleMatcher, RoleMatch
    from src.roles.role_scorer import RoleScorer
    from src.roles.role_definitions import RoleManager, RoleDefinition
    ROLES_AVAILABLE = True
except ImportError:
    ROLES_AVAILABLE = False


class ATSScorer:
    """Main orchestrator for ATS scoring with role-aware capabilities."""
    
    def __init__(self, role_id: Optional[str] = None):
        """
        Initialize ATS scorer with all component scorers.
        
        Args:
            role_id: Specific role to score against (None for auto-detect)
        """
        self.logger = get_logger(__name__)
        
        # Initialize component scorers
        self.section_scorer = SectionScorer()
        self.keyword_scorer = KeywordScorer()
        self.contact_scorer = ContactScorer()
        self.structure_scorer = StructureScorer()
        
        # Initialize role components if available
        self.role_manager = None
        self.role_matcher = None
        self.role_scorer = None
        self.specified_role_id = role_id
        
        if ROLES_AVAILABLE:
            try:
                self.role_manager = RoleManager()
                self.role_matcher = RoleMatcher(self.role_manager)
                self.role_scorer = RoleScorer()
                self.logger.info("Role-aware scoring enabled")
            except Exception as e:
                self.logger.warning(f"Role components not available: {e}")
    
    def score(
        self,
        resume_data: ResumeData,
        role_id: Optional[str] = None
    ) -> ATSScore:
        """
        Calculate complete ATS score for resume.
        
        Args:
            resume_data: Parsed resume data
            role_id: Optional role to score against (overrides init role_id)
            
        Returns:
            ATSScore object with complete scoring results
        """
        start_time = time.time()
        self.logger.info("Starting ATS scoring")
        
        # Determine role
        target_role_id = role_id or self.specified_role_id
        role_match = None
        role_definition = None
        
        if ROLES_AVAILABLE and self.role_matcher:
            if target_role_id:
                # Use specified role
                role_definition = self.role_manager.get_role(target_role_id)
                if role_definition:
                    role_match = RoleMatch(
                        role_id=target_role_id,
                        role_name=role_definition.role_name,
                        confidence=1.0,
                        matching_skills=[],
                        matching_keywords=[],
                        role_definition=role_definition
                    )
                    self.logger.info(f"Using specified role: {role_definition.role_name}")
            else:
                # Auto-detect role
                role_match = self.role_matcher.detect_role(resume_data)
                if role_match:
                    role_definition = role_match.role_definition
        
        # Apply role-specific weights if role detected
        if role_definition and self.role_scorer:
            self._apply_role_weights(role_definition)
        
        # Calculate category scores
        section_category = self.section_scorer.get_category_score(resume_data)
        keyword_category = self.keyword_scorer.get_category_score(resume_data)
        contact_category = self.contact_scorer.get_category_score(resume_data)
        structure_category = self.structure_scorer.get_category_score(resume_data)
        
        # Calculate total score
        total_score = (
            section_category.score +
            keyword_category.score +
            contact_category.score +
            structure_category.score
        )
        
        # Create ATS score object
        ats_score = ATSScore(
            total_score=total_score,
            section_completeness=section_category,
            content_quality=keyword_category,
            contact_information=contact_category,
            structure_organization=structure_category,
            section_scores=self.section_scorer.get_section_scores(resume_data)
        )
        
        # Collect feedback from all scorers
        self._collect_feedback(ats_score, resume_data, role_definition)
        
        # Add metadata
        scoring_time = (time.time() - start_time) * 1000  # ms
        ats_score.scoring_metadata = {
            'scored_at': datetime.now().isoformat(),
            'scoring_time_ms': scoring_time,
            'scorer_version': '3.0.0',  # Phase 3
            'resume_file': resume_data.metadata.file_name if resume_data.metadata else 'unknown',
            'role_detected': role_match.role_name if role_match else None,
            'role_confidence': role_match.confidence if role_match else None
        }
        
        self.logger.info(
            f"ATS scoring complete: {total_score:.2f}/100 "
            f"(Grade: {ats_score.grade}) in {scoring_time:.2f}ms"
        )
        
        return ats_score
    
    def _apply_role_weights(self, role_definition: RoleDefinition) -> None:
        """
        Apply role-specific section weights.
        
        Args:
            role_definition: Role definition with weights
        """
        role_weights = self.role_scorer.get_role_section_weights(role_definition)
        
        # Update section scorer with role weights
        self.section_scorer.config['section_weights'] = role_weights
        
        self.logger.info(f"Applied role weights for {role_definition.role_name}")
    
    def _collect_feedback(
        self,
        ats_score: ATSScore,
        resume_data: ResumeData,
        role_definition: Optional[RoleDefinition] = None
    ) -> None:
        """
        Collect feedback from all scorers.
        
        Args:
            ats_score: ATSScore object to populate
            resume_data: Parsed resume data
            role_definition: Optional role for role-specific feedback
        """
        # Collect from all base scorers
        scorers = [
            self.section_scorer,
            self.keyword_scorer,
            self.contact_scorer,
            self.structure_scorer
        ]
        
        for scorer in scorers:
            feedback = scorer.get_feedback(resume_data)
            
            for strength in feedback.get('strengths', []):
                ats_score.add_strength(strength)
            
            for weakness in feedback.get('weaknesses', []):
                ats_score.add_weakness(weakness)
            
            for suggestion in feedback.get('suggestions', []):
                ats_score.add_suggestion(suggestion)
        
        # Add role-specific feedback
        if role_definition and self.role_scorer:
            role_feedback = self.role_scorer.generate_role_feedback(
                resume_data, role_definition
            )
            
            for strength in role_feedback.get('strengths', []):
                ats_score.add_strength(strength)
            
            for weakness in role_feedback.get('weaknesses', []):
                ats_score.add_weakness(weakness)
            
            for suggestion in role_feedback.get('suggestions', []):
                ats_score.add_suggestion(suggestion)
        
        # Add overall feedback based on total score
        self._add_overall_feedback(ats_score)
    
    def _add_overall_feedback(self, ats_score: ATSScore) -> None:
        """
        Add overall feedback based on total score.
        
        Args:
            ats_score: ATSScore object to populate
        """
        percentage = ats_score.percentage
        
        if percentage >= 90:
            ats_score.add_strength("Excellent ATS-optimized resume")
            ats_score.add_strength("Strong likelihood of passing automated screening")
        elif percentage >= 80:
            ats_score.add_strength("Well-optimized resume with good ATS compatibility")
        elif percentage >= 70:
            ats_score.add_suggestion("Good foundation - addressing key weaknesses will significantly improve ATS compatibility")
        elif percentage >= 60:
            ats_score.add_weakness("Resume needs improvement to pass most ATS systems")
            ats_score.add_suggestion("Focus on adding missing sections and essential keywords")
        else:
            ats_score.add_weakness("Resume may struggle with ATS screening")
            ats_score.add_suggestion("Significant improvements needed - start with section completeness")
        
        # Category-specific guidance
        if ats_score.section_completeness and ats_score.section_completeness.percentage < 70:
            ats_score.add_suggestion("Priority: Improve section completeness (currently {:.0f}%)".format(
                ats_score.section_completeness.percentage
            ))
        
        if ats_score.contact_information and ats_score.contact_information.percentage < 70:
            ats_score.add_suggestion("Priority: Complete contact information (currently {:.0f}%)".format(
                ats_score.contact_information.percentage
            ))