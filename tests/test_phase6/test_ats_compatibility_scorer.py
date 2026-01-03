"""
Unit tests for ATS Compatibility Scorer (Phase 6).
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.ats.ats_compatibility_scorer import ATSCompatibilityScorer


class TestATSCompatibilityScorer(unittest.TestCase):
    """Test integrated ATS compatibility scoring."""
    
    def setUp(self):
        """Initialize ATS scorer for tests."""
        self.scorer = ATSCompatibilityScorer()
    
    @patch('src.ats.format_analyzer.FormatAnalyzer.analyze_file')
    @patch('src.ats.structure_validator.StructureValidator.validate_structure')
    @patch('src.ats.contact_validator.ContactValidator.validate_contact_info')
    @patch('src.ats.keyword_optimizer.KeywordOptimizer.analyze_keywords')
    def test_complete_scoring(self, mock_keywords, mock_contact, mock_structure, mock_format):
        """Test complete ATS scoring pipeline."""
        # Mock all component results
        mock_format.return_value = {
            'format_score': 85.0,
            'is_ats_friendly': True,
            'issues': [],
            'structure_details': {},
            'recommendations': []
        }
        
        mock_structure.return_value = {
            'structure_score': 80.0,
            'is_well_structured': True,
            'required_sections': {'present': [], 'missing': []},
            'recommended_sections': {'present': [], 'missing': []},
            'issues': []
        }
        
        mock_contact.return_value = {
            'contact_score': 90.0,
            'has_complete_contact': True,
            'contact_details': {},
            'issues': []
        }
        
        mock_keywords.return_value = {
            'keyword_score': 75.0,
            'is_optimized': True,
            'metrics': {},
            'keyword_distribution': {},
            'role_keyword_analysis': {},
            'action_verbs': {},
            'issues': []
        }
        
        # Mock extractability
        with patch('src.ats.format_analyzer.FormatAnalyzer.analyze_text_extractability') as mock_extract:
            mock_extract.return_value = {
                'extractability_score': 95.0,
                'is_extractable': True,
                'issues': []
            }
            
            result = self.scorer.score_resume(
                'test.pdf',
                {'summary': 'test'},
                'test text'
            )
        
        self.assertIn('overall_ats_score', result)
        self.assertIn('readiness_level', result)
        self.assertIn('is_ats_ready', result)
        self.assertIn('component_scores', result)
        self.assertGreater(result['overall_ats_score'], 0)
    
    def test_issue_aggregation(self):
        """Test aggregation of issues by severity."""
        format_result = {
            'issues': [
                {'severity': 'critical', 'issue': 'Test critical', 'impact': 'High', 'recommendation': 'Fix'}
            ]
        }
        structure_result = {
            'issues': [
                {'severity': 'high', 'issue': 'Test high', 'impact': 'Medium', 'recommendation': 'Fix'}
            ]
        }
        contact_result = {'issues': []}
        keyword_result = {
            'issues': [
                {'severity': 'medium', 'issue': 'Test medium', 'impact': 'Low', 'recommendation': 'Fix'}
            ]
        }
        extractability_result = {'issues': []}
        
        all_issues = self.scorer._aggregate_issues(
            format_result, structure_result, contact_result,
            keyword_result, extractability_result
        )
        
        self.assertEqual(all_issues['critical_count'], 1)
        self.assertEqual(all_issues['high_count'], 1)
        self.assertEqual(all_issues['medium_count'], 1)
        self.assertEqual(all_issues['total_count'], 3)
    
    def test_readiness_level_determination(self):
        """Test readiness level assignment."""
        # Excellent score
        level = self.scorer._determine_readiness_level(92, {'critical_count': 0})
        self.assertIn('Excellent', level)
        
        # Critical issues
        level = self.scorer._determine_readiness_level(85, {'critical_count': 2})
        self.assertIn('Not Ready', level)
        
        # Poor score
        level = self.scorer._determine_readiness_level(45, {'critical_count': 0})
        self.assertIn('Poor', level)
    
    def test_report_generation(self):
        """Test ATS report generation."""
        analysis_results = {
            'overall_ats_score': 78.5,
            'readiness_level': 'Good',
            'is_ats_ready': True,
            'component_scores': {
                'format': 80.0,
                'structure': 75.0,
                'contact': 85.0,
                'keywords': 70.0,
                'extractability': 90.0
            },
            'issues_by_severity': {
                'total_count': 5,
                'critical_count': 0,
                'high_count': 1,
                'medium_count': 3,
                'low_count': 1
            },
            'recommendations': [
                {
                    'priority': 'high',
                    'order': 1,
                    'category': 'format',
                    'issue': 'Test issue',
                    'action': 'Test action',
                    'impact': 'Test impact'
                }
            ],
            'summary': {
                'score': 78.5,
                'grade': 'C',
                'readiness_level': 'Good',
                'assessment': 'Test assessment',
                'strengths': ['Test strength'],
                'weaknesses': [],
                'total_issues': 5,
                'priority_issues': 1
            }
        }
        
        report = self.scorer.generate_ats_report(analysis_results)
        
        self.assertIsInstance(report, str)
        self.assertIn('ATS COMPATIBILITY', report)
        self.assertIn('78.5', report)
        self.assertIn('Component Breakdown', report)


if __name__ == '__main__':
    unittest.main()