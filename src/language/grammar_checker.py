"""
Grammar and spelling checker using rule-based tools.
Provides explainable grammar issue detection.
"""

import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Optional dependency handling
try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False
    logger.warning("language-tool-python not available. Using basic grammar checks only.")


class GrammarChecker:
    """
    Detects grammar and spelling issues in text.
    Falls back to basic rule-based checks if language_tool is unavailable.
    """
    
    def __init__(self, use_language_tool: bool = True):
        """
        Initialize grammar checker.
        
        Args:
            use_language_tool: Whether to use language_tool_python (requires Java)
        """
        self.use_language_tool = use_language_tool and LANGUAGE_TOOL_AVAILABLE
        self.tool = None
        
        if self.use_language_tool:
            try:
                self.tool = language_tool_python.LanguageTool('en-US')
                logger.info("Grammar checker initialized with LanguageTool")
            except Exception as e:
                logger.warning(f"LanguageTool initialization failed: {e}. Using basic checks.")
                self.use_language_tool = False
    
    def check_text(self, text: str) -> Dict:
        """
        Check text for grammar and spelling issues.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with grammar analysis results
        """
        if not text or not text.strip():
            return self._empty_result()
        
        if self.use_language_tool and self.tool:
            return self._check_with_language_tool(text)
        else:
            return self._check_with_basic_rules(text)
    
    def _check_with_language_tool(self, text: str) -> Dict:
        """Use LanguageTool for comprehensive grammar checking."""
        try:
            matches = self.tool.check(text)
            
            issues = []
            issue_types = {
                'spelling': 0,
                'grammar': 0,
                'punctuation': 0,
                'style': 0
            }
            
            for match in matches:
                issue_type = self._categorize_issue(match.ruleId, match.category)
                issue_types[issue_type] += 1
                
                issues.append({
                    'type': issue_type,
                    'message': match.message,
                    'context': match.context,
                    'severity': self._get_severity(match.category)
                })
            
            total_issues = len(matches)
            
            return {
                'total_issues': total_issues,
                'issue_types': issue_types,
                'issues': issues[:20],  # Limit to first 20 for readability
                'method': 'language_tool'
            }
            
        except Exception as e:
            logger.error(f"LanguageTool check failed: {e}")
            return self._check_with_basic_rules(text)
    
    def _check_with_basic_rules(self, text: str) -> Dict:
        """Fallback to basic rule-based grammar checks."""
        issues = []
        issue_types = {
            'spelling': 0,
            'grammar': 0,
            'punctuation': 0,
            'style': 0
        }
        
        # Check for common issues
        # Double spaces
        if '  ' in text:
            count = text.count('  ')
            issue_types['style'] += count
            issues.append({
                'type': 'style',
                'message': f'Found {count} instances of double spaces',
                'severity': 'minor'
            })
        
        # Missing capitalization after periods
        sentences = re.split(r'[.!?]+\s+', text)
        for sent in sentences:
            if sent and sent[0].islower() and len(sent) > 1:
                issue_types['grammar'] += 1
        
        # Basic spelling check (common typos)
        common_typos = {
            r'\brecieve\b': 'receive',
            r'\boccured\b': 'occurred',
            r'\bseperate\b': 'separate',
            r'\bdefinately\b': 'definitely',
            r'\baccommodate\b': 'accommodate'
        }
        
        for pattern, correct in common_typos.items():
            if re.search(pattern, text, re.IGNORECASE):
                issue_types['spelling'] += 1
                issues.append({
                    'type': 'spelling',
                    'message': f'Possible misspelling (should be "{correct}")',
                    'severity': 'major'
                })
        
        total_issues = sum(issue_types.values())
        
        return {
            'total_issues': total_issues,
            'issue_types': issue_types,
            'issues': issues,
            'method': 'basic_rules'
        }
    
    def _categorize_issue(self, rule_id: str, category: str) -> str:
        """Categorize LanguageTool issue type."""
        category_lower = category.lower()
        
        if 'spell' in category_lower or 'typo' in category_lower:
            return 'spelling'
        elif 'punctuation' in category_lower:
            return 'punctuation'
        elif 'style' in category_lower or 'redundancy' in category_lower:
            return 'style'
        else:
            return 'grammar'
    
    def _get_severity(self, category: str) -> str:
        """Determine severity of grammar issue."""
        if any(word in category.lower() for word in ['error', 'mistake']):
            return 'major'
        elif any(word in category.lower() for word in ['style', 'suggestion']):
            return 'minor'
        else:
            return 'moderate'
    
    def _empty_result(self) -> Dict:
        """Return empty result for missing text."""
        return {
            'total_issues': 0,
            'issue_types': {
                'spelling': 0,
                'grammar': 0,
                'punctuation': 0,
                'style': 0
            },
            'issues': [],
            'method': 'none'
        }
    
    def calculate_grammar_score(self, text: str, max_penalty_per_issue: float = 2.0) -> Dict:
        """
        Calculate grammar score based on detected issues.
        
        Args:
            text: Text to analyze
            max_penalty_per_issue: Maximum penalty per issue
            
        Returns:
            Dict with score and explanation
        """
        if not text or len(text.strip()) < 10:
            return {
                'score': 100.0,
                'explanation': 'Text too short for meaningful analysis'
            }
        
        check_result = self.check_text(text)
        total_issues = check_result['total_issues']
        
        # Calculate penalty based on text length (normalize per 1000 characters)
        text_length = len(text)
        normalized_issues = (total_issues / text_length) * 1000
        
        # Weight by severity
        weighted_issues = (
            check_result['issue_types']['spelling'] * 3.0 +
            check_result['issue_types']['grammar'] * 2.5 +
            check_result['issue_types']['punctuation'] * 1.5 +
            check_result['issue_types']['style'] * 1.0
        )
        
        penalty = min(weighted_issues * max_penalty_per_issue, 50)  # Cap at 50 points
        score = max(100 - penalty, 50)  # Floor at 50
        
        return {
            'score': round(score, 2),
            'total_issues': total_issues,
            'normalized_issues': round(normalized_issues, 2),
            'penalty': round(penalty, 2),
            'issue_breakdown': check_result['issue_types'],
            'explanation': self._generate_explanation(check_result, score)
        }
    
    def _generate_explanation(self, check_result: Dict, score: float) -> str:
        """Generate human-readable explanation of grammar score."""
        total = check_result['total_issues']
        
        if score >= 90:
            return f"Excellent grammar quality with only {total} minor issues detected."
        elif score >= 75:
            return f"Good grammar quality with {total} issues detected."
        elif score >= 60:
            return f"Acceptable grammar with {total} issues that should be reviewed."
        else:
            return f"Grammar needs improvement - {total} issues detected across multiple categories."