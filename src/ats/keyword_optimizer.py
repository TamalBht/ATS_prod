### 4. Keyword Optimizer (`src/ats/keyword_optimizer.py`)

"""
Keyword optimization analyzer for ATS compatibility.
Analyzes keyword usage, density, and placement.
"""

import re
from typing import Dict, List, Set
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class KeywordOptimizer:
    """
    Analyzes keyword optimization for ATS scoring.
    Checks density, relevance, and placement.
    """
    
    def __init__(self):
        """Initialize keyword optimizer."""
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
    
    def analyze_keywords(self, parsed_resume: Dict, role_keywords: List[str] = None) -> Dict:
        """
        Analyze keyword optimization in resume.
        
        Args:
            parsed_resume: Parsed resume dictionary
            role_keywords: Optional list of target role keywords
            
        Returns:
            Dict with keyword analysis results
        """
        # Extract all text from resume
        full_text = self._extract_all_text(parsed_resume)
        
        if not full_text or len(full_text) < 100:
            return self._empty_result()
        
        # Analyze keyword metrics
        word_count = len(full_text.split())
        keyword_density = self._calculate_keyword_density(full_text)
        keyword_distribution = self._analyze_keyword_distribution(parsed_resume)
        
        issues = []
        score = 100
        
        # Check overall keyword density
        if keyword_density < 0.02:  # Less than 2%
            issues.append({
                'severity': 'medium',
                'issue': 'Low keyword density',
                'impact': 'May not match enough job requirements',
                'recommendation': 'Include more industry-specific technical terms and skills'
            })
            score -= 15
        elif keyword_density > 0.10:  # More than 10%
            issues.append({
                'severity': 'high',
                'issue': 'Keyword stuffing detected',
                'impact': 'ATS may penalize for over-optimization',
                'recommendation': 'Reduce repetitive keywords, use natural language'
            })
            score -= 25
        
        # Check keyword distribution across sections
        if keyword_distribution['concentrated']:
            issues.append({
                'severity': 'medium',
                'issue': 'Keywords concentrated in one section',
                'impact': 'Reduces overall ATS matching score',
                'recommendation': 'Distribute keywords naturally across all sections'
            })
            score -= 10
        
        # Analyze role-specific keywords if provided
        role_analysis = {}
        if role_keywords:
            role_analysis = self._analyze_role_keywords(full_text, role_keywords)
            
            missing_ratio = role_analysis['missing_count'] / max(len(role_keywords), 1)
            if missing_ratio > 0.5:
                issues.append({
                    'severity': 'high',
                    'issue': f"Missing {role_analysis['missing_count']} of {len(role_keywords)} target keywords",
                    'impact': 'Low match rate with job requirements',
                    'recommendation': 'Incorporate more job-specific keywords from job description'
                })
                score -= 20
            elif missing_ratio > 0.3:
                issues.append({
                    'severity': 'medium',
                    'issue': f"Missing {role_analysis['missing_count']} target keywords",
                    'impact': 'Moderate match rate with job requirements',
                    'recommendation': 'Add missing keywords where relevant to your experience'
                })
                score -= 10
        
        # Check for action verbs
        action_verb_analysis = self._analyze_action_verbs(full_text)
        if action_verb_analysis['count'] < 5:
            issues.append({
                'severity': 'medium',
                'issue': 'Few action verbs detected',
                'impact': 'Weak impact statements reduce ATS scoring',
                'recommendation': 'Start bullet points with strong action verbs (led, developed, improved)'
            })
            score -= 10
        
        return {
            'keyword_score': max(0, round(score, 2)),
            'is_optimized': score >= 70,
            'metrics': {
                'word_count': word_count,
                'keyword_density': round(keyword_density, 4),
                'unique_keywords': keyword_distribution['unique_count'],
                'action_verbs': action_verb_analysis['count']
            },
            'keyword_distribution': keyword_distribution,
            'role_keyword_analysis': role_analysis,
            'action_verbs': action_verb_analysis,
            'issues': issues,
            'recommendations': self._generate_keyword_recommendations(issues, role_analysis)
        }
    
    def _extract_all_text(self, parsed_resume: Dict) -> str:
        """Extract all text content from parsed resume."""
        all_text = []
        
        for key, value in parsed_resume.items():
            if key in ['metadata', 'raw_text']:
                continue
            
            if isinstance(value, str):
                all_text.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        all_text.append(item)
                    elif isinstance(item, dict):
                        all_text.extend(str(v) for v in item.values() if isinstance(v, str))
            elif isinstance(value, dict):
                all_text.extend(str(v) for v in value.values() if isinstance(v, str))
        
        return " ".join(all_text)
    
    def _calculate_keyword_density(self, text: str) -> float:
        """Calculate technical keyword density."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        if not words:
            return 0.0
        
        # Filter stopwords
        meaningful_words = [w for w in words if w not in self.stopwords]
        
        # Count technical/domain keywords (capitalized in original, or common tech terms)
        technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms (API, REST, SQL)
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b',  # CamelCase (JavaScript)
        ]
        
        technical_count = 0
        for pattern in technical_patterns:
            technical_count += len(re.findall(pattern, text))
        
        # Also count common technical terms
        tech_terms = {
            'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws',
            'docker', 'kubernetes', 'api', 'rest', 'microservices', 'agile',
            'scrum', 'git', 'ci/cd', 'devops', 'cloud', 'database'
        }
        
        technical_count += sum(1 for word in meaningful_words if word in tech_terms)
        
        return technical_count / len(words) if words else 0.0
    
    def _analyze_keyword_distribution(self, parsed_resume: Dict) -> Dict:
        """Analyze how keywords are distributed across sections."""
        section_keyword_counts = {}
        total_keywords = 0
        
        for section_name, section_data in parsed_resume.items():
            if section_name in ['metadata', 'raw_text']:
                continue
            
            section_text = self._extract_section_text(section_data)
            if not section_text:
                continue
            
            keywords = self._extract_keywords(section_text)
            section_keyword_counts[section_name] = len(keywords)
            total_keywords += len(keywords)
        
        # Check if keywords are concentrated (>60% in one section)
        concentrated = False
        if section_keyword_counts:
            max_section_count = max(section_keyword_counts.values())
            if total_keywords > 0 and max_section_count / total_keywords > 0.6:
                concentrated = True
        
        return {
            'section_counts': section_keyword_counts,
            'total_keywords': total_keywords,
            'unique_count': len(set(self._extract_keywords(self._extract_all_text(parsed_resume)))),
            'concentrated': concentrated
        }
    
    def _extract_section_text(self, section_data) -> str:
        """Extract text from a section."""
        if isinstance(section_data, str):
            return section_data
        elif isinstance(section_data, list):
            texts = []
            for item in section_data:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict):
                    texts.extend(str(v) for v in item.values() if isinstance(v, str))
            return " ".join(texts)
        elif isinstance(section_data, dict):
            return " ".join(str(v) for v in section_data.values() if isinstance(v, str))
        return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in self.stopwords and len(w) > 3]
        return keywords
    
    def _analyze_role_keywords(self, text: str, role_keywords: List[str]) -> Dict:
        """Analyze presence of role-specific keywords."""
        text_lower = text.lower()
        
        found_keywords = []
        missing_keywords = []
        keyword_frequencies = {}
        
        for keyword in role_keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            
            if count > 0:
                found_keywords.append(keyword)
                keyword_frequencies[keyword] = count
            else:
                missing_keywords.append(keyword)
        
        match_rate = len(found_keywords) / len(role_keywords) if role_keywords else 0
        
        return {
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords,
            'match_rate': round(match_rate, 2),
            'found_count': len(found_keywords),
            'missing_count': len(missing_keywords),
            'keyword_frequencies': keyword_frequencies
        }
    
    def _analyze_action_verbs(self, text: str) -> Dict:
        """Analyze use of strong action verbs."""
        strong_action_verbs = {
            'led', 'developed', 'created', 'implemented', 'designed', 'built',
            'managed', 'improved', 'increased', 'reduced', 'optimized', 'achieved',
            'delivered', 'launched', 'established', 'directed', 'coordinated',
            'executed', 'generated', 'accelerated', 'transformed', 'pioneered'
        }
        
        text_lower = text.lower()
        found_verbs = []
        verb_frequencies = {}
        
        for verb in strong_action_verbs:
            # Look for verb at start of sentences/bullets
            pattern = r'(?:^|\n|\r\n|[•\.\-])\s*' + verb + r'\b'


            matches = re.findall(pattern, text_lower, re.MULTILINE)
            if matches:
                found_verbs.append(verb)
                verb_frequencies[verb] = len(matches)
        
        return {
            'count': len(found_verbs),
            'verbs': found_verbs,
            'frequencies': verb_frequencies
        }
    
    def _generate_keyword_recommendations(self, issues: List[Dict], role_analysis: Dict) -> List[str]:
        """Generate keyword optimization recommendations."""
        recommendations = []
        
        if any('stuffing' in i['issue'].lower() for i in issues):
            recommendations.append("Reduce keyword repetition - use natural, varied language")
        
        if any('low keyword' in i['issue'].lower() for i in issues):
            recommendations.append("Include more technical terms and industry-specific keywords")
        
        if role_analysis and role_analysis.get('missing_keywords'):
            top_missing = role_analysis['missing_keywords'][:5]
            recommendations.append(
                f"Add these job-relevant keywords: {', '.join(top_missing)}"
            )
        
        if any('action verbs' in i['issue'].lower() for i in issues):
            recommendations.append(
                "Start achievement bullets with strong action verbs (Led, Developed, Improved)"
            )
        
        if not issues:
            recommendations.append("Keyword usage is well-optimized for ATS")
        
        return recommendations
    
    def _empty_result(self) -> Dict:
        return {
        'keyword_score': 0,
        'is_optimized': False,
        'metrics': {
            'word_count': 0,
            'keyword_density': 0.0,
            'unique_keywords': 0,
            'action_verbs': 0
        },
        'keyword_distribution': {
            'section_counts': {},
            'total_keywords': 0,
            'unique_count': 0,
            'concentrated': False
        },
        'role_keyword_analysis': {},
        'action_verbs': {},
        'issues': [{
            'severity': 'critical',
            'issue': 'Insufficient text content',
            'impact': 'Cannot analyze keywords',
            'recommendation': 'Ensure resume has substantial content'
        }],
        'recommendations': ['Add meaningful content to resume']
    }
