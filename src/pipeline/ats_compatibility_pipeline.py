"""
ATS Compatibility Pipeline - Phase 6
Orchestrates layout detection, structure validation, and compatibility scoring.
"""

import json
from pathlib import Path
from typing import Dict, Optional

from ..models.resume_data import ResumeData
from ..models.ats_compatibility import (
    ATSCompatibilityResult,
    CompatibilityWarning,
    RiskLevel,
    WarningType
)
from ..analysis.layout_detector import LayoutDetector
from ..analysis.structure_validator import StructureValidator
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ATSCompatibilityPipeline:
    """
    Phase 6: ATS Compatibility Analysis Pipeline
    
    Evaluates whether a resume can be safely parsed by ATS systems.
    """
    
    def __init__(self):
        self.layout_detector = LayoutDetector()
        self.structure_validator = StructureValidator()
    
    def analyze(
        self, 
        resume_data: ResumeData,
        file_path: str
    ) -> ATSCompatibilityResult:
        """
        Perform complete ATS compatibility analysis.
        
        Args:
            resume_data: Parsed resume data
            file_path: Path to original resume file
            
        Returns:
            ATSCompatibilityResult with risk assessment and warnings
        """
        logger.info("Starting ATS compatibility analysis")
        
        # Initialize result
        result = ATSCompatibilityResult(
            risk_level=RiskLevel.LOW.value,
            overall_score=100.0,
            file_format=Path(file_path).suffix.lower()
        )
        
        # 1. Layout Detection
        layout_issues = self.layout_detector.analyze_file(file_path)
        result.layout_issues = layout_issues
        
        # Process layout issues
        self._process_layout_issues(layout_issues, result)
        
        # 2. Structure Validation
        structure_results = self.structure_validator.validate_structure(resume_data)
        
        # Process structure validation
        self._process_structure_validation(structure_results, result)
        
        # 3. Calculate overall risk level
        result.risk_level = self._calculate_risk_level(result)
        
        # 4. Calculate overall score
        result.overall_score = self._calculate_compatibility_score(result)
        
        logger.info(
            f"ATS compatibility analysis complete: {result.risk_level} "
            f"(score: {result.overall_score})"
        )
        
        return result
    
    def _process_layout_issues(
        self, 
        layout_issues: list,
        result: ATSCompatibilityResult
    ) -> None:
        """Process detected layout issues and generate warnings"""
        
        for issue in layout_issues:
            if issue.issue_type == "TABLES":
                result.has_tables = True
                result.warnings.append(CompatibilityWarning(
                    type=WarningType.TABLES.value,
                    severity=RiskLevel.MEDIUM.value,
                    message=f"Resume contains {issue.count} table(s)",
                    impact="ATS may struggle to extract text from table cells",
                    recommendation="Convert tables to simple text with bullet points"
                ))
            
            elif issue.issue_type == "MULTI_COLUMN_LAYOUT":
                result.has_multi_column = True
                result.warnings.append(CompatibilityWarning(
                    type=WarningType.MULTI_COLUMN.value,
                    severity=RiskLevel.HIGH.value,
                    message="Multi-column layout detected",
                    location=f"Page {issue.page_number}" if issue.page_number else None,
                    impact="ATS may read columns left-to-right, scrambling content order",
                    recommendation="Use single-column layout for maximum compatibility"
                ))
            
            elif issue.issue_type == "IMAGES":
                result.has_images = True
                result.warnings.append(CompatibilityWarning(
                    type=WarningType.IMAGES.value,
                    severity=RiskLevel.MEDIUM.value,
                    message=f"Resume contains {issue.count} image(s)",
                    location=f"Page {issue.page_number}" if issue.page_number else None,
                    impact="Images cannot be parsed by ATS and may contain important info",
                    recommendation="Remove images/icons or ensure text equivalents exist"
                ))
            
            elif issue.issue_type == "TEXT_BOXES":
                result.has_text_boxes = True
                result.warnings.append(CompatibilityWarning(
                    type=WarningType.TEXT_BOXES.value,
                    severity=RiskLevel.HIGH.value,
                    message=f"Resume contains {issue.count} text box(es)",
                    impact="Text boxes may be ignored or read out of order by ATS",
                    recommendation="Move all text to main document body"
                ))
            
            elif issue.issue_type == "HEADERS_FOOTERS":
                result.has_headers_footers = True
                result.warnings.append(CompatibilityWarning(
                    type=WarningType.HEADERS_FOOTERS.value,
                    severity=RiskLevel.LOW.value,
                    message="Resume contains headers or footers",
                    impact="Header/footer content may not be parsed correctly",
                    recommendation="Move critical information to main document body"
                ))
            
            elif issue.issue_type == "POTENTIAL_TABLE":
                if not result.has_tables:  # Don't double-warn
                    result.warnings.append(CompatibilityWarning(
                        type=WarningType.TABLES.value,
                        severity=RiskLevel.MEDIUM.value,
                        message="Possible table-like formatting detected",
                        location=f"Page {issue.page_number}" if issue.page_number else None,
                        impact="May indicate complex formatting that ATS struggles with",
                        recommendation="Verify layout is ATS-friendly"
                    ))
    
    def _process_structure_validation(
        self,
        structure_results: Dict,
        result: ATSCompatibilityResult
    ) -> None:
        """Process structure validation results"""
        
        result.section_order_valid = structure_results["section_order_valid"]
        result.missing_standard_sections = (
            structure_results["missing_critical_sections"]
        )
        
        # Generate warnings for missing critical sections
        for section in structure_results["missing_critical_sections"]:
            result.warnings.append(CompatibilityWarning(
                type=WarningType.UNUSUAL_STRUCTURE.value,
                severity=RiskLevel.HIGH.value,
                message=f"Missing critical section: {section.title()}",
                impact="ATS may reject resume without standard sections",
                recommendation=f"Add a {section.title()} section"
            ))
        
        # Generate warnings for order issues
        if structure_results["order_issues"]:
            result.warnings.append(CompatibilityWarning(
                type=WarningType.SECTION_ORDER.value,
                severity=RiskLevel.LOW.value,
                message="Non-standard section ordering detected",
                impact="May reduce parsing accuracy",
                recommendation="Reorder: Contact → Summary → Experience → Education → Skills"
            ))
        
        # Generate warning for unusual structure
        if structure_results["unusual_structure"]:
            result.warnings.append(CompatibilityWarning(
                type=WarningType.UNUSUAL_STRUCTURE.value,
                severity=RiskLevel.MEDIUM.value,
                message="Resume has unusual structure (too few sections)",
                impact="May not be recognized as a standard resume",
                recommendation="Add standard sections to improve recognition"
            ))
    
    def _calculate_risk_level(self, result: ATSCompatibilityResult) -> str:
        """Calculate overall risk level based on warnings"""
        
        high_severity_count = sum(
            1 for w in result.warnings 
            if w.severity == RiskLevel.HIGH.value
        )
        medium_severity_count = sum(
            1 for w in result.warnings 
            if w.severity == RiskLevel.MEDIUM.value
        )
        
        if high_severity_count >= 2 or result.has_text_boxes or result.has_multi_column:
            return RiskLevel.HIGH.value
        elif high_severity_count >= 1 or medium_severity_count >= 2:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value
    
    def _calculate_compatibility_score(
        self, 
        result: ATSCompatibilityResult
    ) -> float:
        """Calculate numerical compatibility score (0-100)"""
        
        score = 100.0
        
        # Deduct for each warning based on severity
        for warning in result.warnings:
            if warning.severity == RiskLevel.HIGH.value:
                score -= 20.0
            elif warning.severity == RiskLevel.MEDIUM.value:
                score -= 10.0
            elif warning.severity == RiskLevel.LOW.value:
                score -= 5.0
        
        # Hard penalties for specific critical issues
        if result.has_text_boxes:
            score -= 10.0  # Additional penalty
        
        if result.has_multi_column:
            score -= 10.0  # Additional penalty
        
        return max(0.0, score)
    
    def save_results(
        self,
        result: ATSCompatibilityResult,
        output_path: str
    ) -> None:
        """
        Save ATS compatibility results to JSON file.
        
        Args:
            result: ATSCompatibilityResult to save
            output_path: Path to output JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"ATS compatibility results saved to {output_file}")