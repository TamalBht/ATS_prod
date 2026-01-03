"""
Main ATS Compatibility Scorer - Aggregates all ATS analysis components.
Provides comprehensive ATS compatibility assessment.
"""

from typing import Dict, List
import logging
from pathlib import Path

from src.ats.format_analyzer import FormatAnalyzer
from src.ats.structure_validator import StructureValidator
from src.ats.contact_validator import ContactValidator
from src.ats.keyword_optimizer import KeywordOptimizer

logger = logging.getLogger(__name__)


class ATSCompatibilityScorer:
    """
    Main ATS compatibility scorer.
    Combines format, structure, contact, and keyword analysis.
    """
    
    def __init__(self):
        """Initialize ATS compatibility scorer with all components."""
        self.format_analyzer = FormatAnalyzer()
        self.structure_validator = StructureValidator()
        self.contact_validator = ContactValidator()
        self.keyword_optimizer = KeywordOptimizer()
        
        logger.info("ATS Compatibility Scorer initialized")
    
    def score_resume(self, resume_path: str, parsed_resume: Dict, 
                    raw_text: str = "", role_keywords: List[str] = None) -> Dict:
        """
        Perform comprehensive ATS compatibility analysis.
        
        Args:
            resume_path: Path to resume file
            parsed_resume: Parsed resume dictionary from Phase 1
            raw_text: Raw extracted text
            role_keywords: Optional list of target role keywords
            
        Returns:
            Dict with complete ATS compatibility analysis
        """
        logger.info(f"Starting ATS compatibility analysis for: {resume_path}")
        
        # Run all analyses
        format_result = self.format_analyzer.analyze_file(resume_path)
        structure_result = self.structure_validator.validate_structure(parsed_resume)
        contact_result = self.contact_validator.validate_contact_info(parsed_resume, raw_text)
        keyword_result = self.keyword_optimizer.analyze_keywords(parsed_resume, role_keywords)
        
        # Analyze text extractability
        if raw_text:
            extractability_result = self.format_analyzer.analyze_text_extractability(raw_text)
        else:
            extractability_result = {'extractability_score': 100, 'is_extractable': True, 'issues': []}
        
        # Calculate weighted overall score
        # Format: 30%, Structure: 25%, Contact: 15%, Keywords: 20%, Extractability: 10%
        overall_score = (
            format_result['format_score'] * 0.30 +
            structure_result['structure_score'] * 0.25 +
            contact_result['contact_score'] * 0.15 +
            keyword_result['keyword_score'] * 0.20 +
            extractability_result['extractability_score'] * 0.10
        )
        
        # Aggregate all issues by severity
        all_issues = self._aggregate_issues(
            format_result, structure_result, contact_result, 
            keyword_result, extractability_result
        )
        
        # Generate comprehensive recommendations
        recommendations = self._generate_comprehensive_recommendations(
            format_result, structure_result, contact_result, keyword_result, all_issues
        )
        
        # Determine ATS readiness level
        readiness_level = self._determine_readiness_level(overall_score, all_issues)
        
        return {
            'overall_ats_score': round(overall_score, 2),
            'readiness_level': readiness_level,
            'is_ats_ready': overall_score >= 70,
            'component_scores': {
                'format': format_result['format_score'],
                'structure': structure_result['structure_score'],
                'contact': contact_result['contact_score'],
                'keywords': keyword_result['keyword_score'],
                'extractability': extractability_result['extractability_score']
            },
            'detailed_analysis': {
                'format': format_result,
                'structure': structure_result,
                'contact': contact_result,
                'keywords': keyword_result,
                'extractability': extractability_result
            },
            'issues_by_severity': all_issues,
            'recommendations': recommendations,
            'summary': self._generate_summary(overall_score, all_issues, readiness_level)
        }
    
    def _aggregate_issues(self, format_result: Dict, structure_result: Dict,
                         contact_result: Dict, keyword_result: Dict,
                         extractability_result: Dict) -> Dict:
        """Aggregate and categorize all issues by severity."""
        all_issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Collect issues from all components
        for result in [format_result, structure_result, contact_result, 
                      keyword_result, extractability_result]:
            if 'issues' in result:
                for issue in result['issues']:
                    severity = issue.get('severity', 'medium')
                    all_issues[severity].append(issue)
        
        # Add counts
        all_issues['total_count'] = sum(len(issues) for issues in all_issues.values() if isinstance(issues, list))
        all_issues['critical_count'] = len(all_issues['critical'])
        all_issues['high_count'] = len(all_issues['high'])
        all_issues['medium_count'] = len(all_issues['medium'])
        all_issues['low_count'] = len(all_issues['low'])
        
        return all_issues
    
    def _generate_comprehensive_recommendations(self, format_result: Dict, 
                                               structure_result: Dict,
                                               contact_result: Dict,
                                               keyword_result: Dict,
                                               all_issues: Dict) -> List[Dict]:
        """Generate prioritized, actionable recommendations."""
        recommendations = []
        priority_counter = {'critical': 1, 'high': 1, 'medium': 1, 'low': 1}
        
        # Critical recommendations (must fix)
        if all_issues['critical']:
            for issue in all_issues['critical']:
                recommendations.append({
                    'priority': 'critical',
                    'order': priority_counter['critical'],
                    'category': self._categorize_issue(issue),
                    'issue': issue['issue'],
                    'action': issue['recommendation'],
                    'impact': issue['impact']
                })
                priority_counter['critical'] += 1
        
        # High priority recommendations
        if all_issues['high']:
            for issue in all_issues['high'][:5]:  # Top 5 high priority
                recommendations.append({
                    'priority': 'high',
                    'order': priority_counter['high'],
                    'category': self._categorize_issue(issue),
                    'issue': issue['issue'],
                    'action': issue['recommendation'],
                    'impact': issue['impact']
                })
                priority_counter['high'] += 1
        
        # Medium priority recommendations
        if all_issues['medium']:
            for issue in all_issues['medium'][:3]:  # Top 3 medium priority
                recommendations.append({
                    'priority': 'medium',
                    'order': priority_counter['medium'],
                    'category': self._categorize_issue(issue),
                    'issue': issue['issue'],
                    'action': issue['recommendation'],
                    'impact': issue['impact']
                })
                priority_counter['medium'] += 1
        
        # Add general best practices if score is good
        if all_issues['total_count'] <= 3:
            recommendations.append({
                'priority': 'low',
                'order': 1,
                'category': 'optimization',
                'issue': 'Resume is ATS-compatible',
                'action': 'Consider tailoring keywords for specific job postings',
                'impact': 'Maximizes match rate with different roles'
            })
        
        return recommendations
    
    def _categorize_issue(self, issue: Dict) -> str:
        """Categorize issue by type."""
        issue_text = issue['issue'].lower()
        
        if any(word in issue_text for word in ['format', 'file', 'pdf', 'docx', 'table', 'image', 'column']):
            return 'format'
        elif any(word in issue_text for word in ['section', 'structure', 'missing']):
            return 'structure'
        elif any(word in issue_text for word in ['contact', 'email', 'phone', 'name']):
            return 'contact'
        elif any(word in issue_text for word in ['keyword', 'density', 'action verb']):
            return 'keywords'
        else:
            return 'general'
    
    def _determine_readiness_level(self, score: float, all_issues: Dict) -> str:
        """Determine ATS readiness level based on score and issues."""
        if all_issues['critical_count'] > 0:
            return "Not Ready - Critical Issues"
        elif score >= 90:
            return "Excellent - ATS Optimized"
        elif score >= 80:
            return "Very Good - ATS Ready"
        elif score >= 70:
            return "Good - Minor Improvements Needed"
        elif score >= 60:
            return "Fair - Several Issues to Address"
        else:
            return "Poor - Major Improvements Required"
    
    def _generate_summary(self, score: float, all_issues: Dict, readiness_level: str) -> Dict:
        """Generate executive summary of ATS analysis."""
        # Determine grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        # Generate assessment message
        if score >= 85:
            assessment = "Your resume is well-optimized for ATS systems. Focus on tailoring keywords for specific jobs."
        elif score >= 70:
            assessment = "Your resume is ATS-compatible with room for improvement. Address flagged issues for better results."
        elif score >= 55:
            assessment = "Your resume has moderate ATS compatibility issues. Prioritize high-severity fixes."
        else:
            assessment = "Your resume needs significant work to pass ATS screening. Start with critical issues."
        
        # Key strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if all_issues['critical_count'] == 0:
            strengths.append("No critical blocking issues")
        else:
            weaknesses.append(f"{all_issues['critical_count']} critical issue(s) blocking ATS")
        
        if all_issues['high_count'] <= 2:
            strengths.append("Few high-priority issues")
        elif all_issues['high_count'] > 5:
            weaknesses.append(f"{all_issues['high_count']} high-priority issues detected")
        
        if all_issues['total_count'] <= 5:
            strengths.append("Generally clean structure")
        elif all_issues['total_count'] > 15:
            weaknesses.append("Multiple formatting and content issues")
        
        return {
            'score': score,
            'grade': grade,
            'readiness_level': readiness_level,
            'assessment': assessment,
            'strengths': strengths if strengths else ["See recommendations for improvements"],
            'weaknesses': weaknesses if weaknesses else ["No major weaknesses detected"],
            'total_issues': all_issues['total_count'],
            'priority_issues': all_issues['critical_count'] + all_issues['high_count']
        }
    
    def generate_ats_report(self, analysis_results: Dict) -> str:
        """
        Generate human-readable ATS compatibility report.
        
        Args:
            analysis_results: Results from score_resume()
            
        Returns:
            Formatted text report
        """
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("ATS COMPATIBILITY ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Summary
        summary = analysis_results['summary']
        report_lines.append(f"Overall ATS Score: {summary['score']:.1f}/100 (Grade: {summary['grade']})")
        report_lines.append(f"Readiness Level: {summary['readiness_level']}")
        report_lines.append(f"ATS Ready: {'YES' if analysis_results['is_ats_ready'] else 'NO'}")
        report_lines.append("")
        report_lines.append(f"Assessment: {summary['assessment']}")
        report_lines.append("")
        
        # Component Scores
        report_lines.append("Component Breakdown:")
        report_lines.append("-" * 80)
        for component, score in analysis_results['component_scores'].items():
            bar = "█" * int(score/5) + "░" * (20 - int(score/5))
            report_lines.append(f"  {component.capitalize():20} [{bar}] {score:.1f}/100")
        report_lines.append("")
        
        # Issues Summary
        issues = analysis_results['issues_by_severity']
        report_lines.append(f"Issues Detected: {issues['total_count']}")
        report_lines.append(f"  Critical: {issues['critical_count']}")
        report_lines.append(f"  High:     {issues['high_count']}")
        report_lines.append(f"  Medium:   {issues['medium_count']}")
        report_lines.append(f"  Low:      {issues['low_count']}")
        report_lines.append("")
        
        # Priority Recommendations
        report_lines.append("TOP PRIORITY ACTIONS:")
        report_lines.append("=" * 80)
        
        recommendations = analysis_results['recommendations']
        critical_recs = [r for r in recommendations if r['priority'] == 'critical']
        high_recs = [r for r in recommendations if r['priority'] == 'high']
        
        if critical_recs:
            report_lines.append("\n🔴 CRITICAL (Fix Immediately):")
            for rec in critical_recs:
                report_lines.append(f"\n  {rec['order']}. {rec['issue']}")
                report_lines.append(f"     → {rec['action']}")
                report_lines.append(f"     Impact: {rec['impact']}")
        
        if high_recs:
            report_lines.append("\n🟠 HIGH PRIORITY (Fix Soon):")
            for rec in high_recs[:3]:  # Top 3
                report_lines.append(f"\n  {rec['order']}. {rec['issue']}")
                report_lines.append(f"     → {rec['action']}")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)