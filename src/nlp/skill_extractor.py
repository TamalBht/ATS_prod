"""
Enhanced skill extraction using NLP techniques
"""

from typing import List, Set, Dict, Tuple
import re

from src.nlp.text_vectorizer import TextVectorizer
from src.utils.logger import get_logger


class SkillExtractor:
    """Extracts skills from resume text using NLP."""
    
    # Common technical skill patterns
    SKILL_PATTERNS = {
        'programming_languages': [
            r'\b(Python|Java|JavaScript|C\+\+|C#|Ruby|Go|Rust|Swift|Kotlin|PHP|TypeScript)\b',
            r'\b(Scala|Perl|R|MATLAB|Julia|Haskell|Elixir|Clojure)\b'
        ],
        'frameworks': [
            r'\b(React|Angular|Vue\.js|Django|Flask|Spring|Express|FastAPI|Node\.js)\b',
            r'\b(Ruby on Rails|ASP\.NET|Laravel|Symfony|Next\.js|Nuxt\.js)\b',
            r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy)\b'
        ],
        'databases': [
            r'\b(PostgreSQL|MySQL|MongoDB|Redis|Cassandra|Oracle|SQL Server)\b',
            r'\b(DynamoDB|Elasticsearch|Neo4j|CouchDB|MariaDB|SQLite)\b'
        ],
        'cloud_devops': [
            r'\b(AWS|Azure|GCP|Google Cloud|Docker|Kubernetes|Jenkins|GitLab CI)\b',
            r'\b(Terraform|Ansible|Chef|Puppet|CircleCI|Travis CI|GitHub Actions)\b',
            r'\b(ECS|EKS|Lambda|EC2|S3|RDS|CloudFormation)\b'
        ],
        'tools': [
            r'\b(Git|GitHub|GitLab|Bitbucket|Jira|Confluence|Slack)\b',
            r'\b(VS Code|IntelliJ|PyCharm|Eclipse|Vim|Emacs)\b',
            r'\b(Postman|Swagger|Insomnia|DataGrip|Tableau|Power BI)\b'
        ]
    }
    
    # Common skill delimiters in resumes
    SKILL_DELIMITERS = [',', '•', '|', '/', ';', '\n', '·']
    
    def __init__(self):
        """Initialize skill extractor."""
        self.logger = get_logger(__name__)
        self.vectorizer = TextVectorizer()
    
    def extract_skills(
        self,
        text: str,
        use_patterns: bool = True,
        use_tfidf: bool = True,
        use_context: bool = True
    ) -> List[str]:
        """
        Extract skills from text using multiple methods.
        
        Args:
            text: Resume text
            use_patterns: Use regex pattern matching
            use_tfidf: Use TF-IDF for extraction
            use_context: Use context-based extraction
            
        Returns:
            List of extracted skills
        """
        skills = set()
        
        # Method 1: Pattern-based extraction
        if use_patterns:
            pattern_skills = self._extract_with_patterns(text)
            skills.update(pattern_skills)
            self.logger.debug(f"Pattern extraction: {len(pattern_skills)} skills")
        
        # Method 2: TF-IDF based extraction
        if use_tfidf:
            tfidf_skills = self._extract_with_tfidf(text)
            skills.update(tfidf_skills)
            self.logger.debug(f"TF-IDF extraction: {len(tfidf_skills)} skills")
        
        # Method 3: Context-based extraction
        if use_context:
            context_skills = self._extract_from_skills_section(text)
            skills.update(context_skills)
            self.logger.debug(f"Context extraction: {len(context_skills)} skills")
        
        # Clean and deduplicate
        cleaned_skills = self._clean_skills(list(skills))
        
        self.logger.info(f"Extracted {len(cleaned_skills)} unique skills")
        return cleaned_skills
    
    def _extract_with_patterns(self, text: str) -> Set[str]:
        """
        Extract skills using regex patterns.
        
        Args:
            text: Resume text
            
        Returns:
            Set of skills
        """
        skills = set()
        
        for category, patterns in self.SKILL_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    skill = match.group(0)
                    # Preserve original casing for acronyms
                    if skill.isupper() or any(c.isupper() for c in skill):
                        skills.add(skill)
                    else:
                        skills.add(skill.title())
        
        return skills
    
    def _extract_with_tfidf(self, text: str) -> Set[str]:
        """
        Extract skills using TF-IDF importance.
        
        Args:
            text: Resume text
            
        Returns:
            Set of skills
        """
        skills = set()
        
        # Extract important terms
        keywords = self.vectorizer.extract_keywords_tfidf(text, top_n=100)
        
        for keyword, score in keywords:
            # Filter for skill-like terms
            if self._is_skill_like(keyword):
                skills.add(self._normalize_skill(keyword))
        
        return skills
    
    def _extract_from_skills_section(self, text: str) -> Set[str]:
        """
        Extract skills from explicit skills section.
        
        Args:
            text: Resume text
            
        Returns:
            Set of skills
        """
        skills = set()
        
        # Find skills section
        skills_section = self._find_skills_section(text)
        
        if not skills_section:
            return skills
        
        # Try different delimiters
        for delimiter in self.SKILL_DELIMITERS:
            if delimiter in skills_section:
                parts = skills_section.split(delimiter)
                for part in parts:
                    cleaned = part.strip()
                    if self._is_valid_skill(cleaned):
                        skills.add(self._normalize_skill(cleaned))
        
        return skills
    
    def _find_skills_section(self, text: str) -> str:
        """
        Find and extract the skills section from text.
        
        Args:
            text: Resume text
            
        Returns:
            Skills section text or empty string
        """
        # Look for skills header
        lines = text.split('\n')
        
        skills_header_patterns = [
            r'^skills?\s*:?\s*$',
            r'^technical\s+skills?\s*:?\s*$',
            r'^core\s+competencies\s*:?\s*$',
            r'^technologies\s*:?\s*$',
            r'^expertise\s*:?\s*$'
        ]
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            for pattern in skills_header_patterns:
                if re.match(pattern, line_lower):
                    # Found skills header, extract content until next section
                    section_content = []
                    for j in range(i + 1, min(i + 20, len(lines))):
                        next_line = lines[j].strip()
                        
                        # Stop at next section header (all caps or ends with colon)
                        if (next_line.isupper() and len(next_line) > 3) or \
                           (next_line.endswith(':') and len(next_line) < 50):
                            break
                        
                        if next_line:
                            section_content.append(next_line)
                    
                    return ' '.join(section_content)
        
        return ""
    
    def _is_skill_like(self, term: str) -> bool:
        """
        Check if term looks like a skill.
        
        Args:
            term: Term to check
            
        Returns:
            True if skill-like
        """
        # Multi-word technical terms
        if len(term.split()) >= 2:
            return True
        
        # Single words that are capitalized or contain special chars
        if any(c.isupper() for c in term) or any(c in term for c in ['.', '+', '#']):
            return True
        
        # Longer technical-sounding words
        if len(term) > 8:
            return True
        
        return False
    
    def _is_valid_skill(self, skill: str) -> bool:
        """
        Validate if extracted text is a valid skill.
        
        Args:
            skill: Skill to validate
            
        Returns:
            True if valid
        """
        # Remove common non-skill words
        stopwords = {
            'experience', 'knowledge', 'understanding', 'ability',
            'skills', 'proficient', 'familiar', 'strong', 'good',
            'excellent', 'basic', 'advanced', 'and', 'or', 'with'
        }
        
        skill_lower = skill.lower()
        
        # Skip if only stopwords
        if skill_lower in stopwords:
            return False
        
        # Must have reasonable length
        if len(skill) < 2 or len(skill) > 50:
            return False
        
        # Must contain at least one letter
        if not any(c.isalpha() for c in skill):
            return False
        
        return True
    
    def _normalize_skill(self, skill: str) -> str:
        """
        Normalize skill name.
        
        Args:
            skill: Skill to normalize
            
        Returns:
            Normalized skill
        """
        # Remove leading/trailing punctuation
        skill = skill.strip('•-*.,;: ')
        
        # Preserve common technical formats
        if skill.upper() in ['C++', 'C#', 'HTML', 'CSS', 'SQL', 'API', 'AWS', 'GCP']:
            return skill.upper()
        
        # Preserve mixed case for frameworks
        known_mixed_case = [
            'JavaScript', 'TypeScript', 'Node.js', 'Next.js', 'Vue.js',
            'MongoDB', 'PostgreSQL', 'MySQL', 'GraphQL', 'GitHub', 'GitLab'
        ]
        
        skill_lower = skill.lower()
        for known in known_mixed_case:
            if known.lower() == skill_lower:
                return known
        
        # Default: title case
        return skill.title()
    
    def _clean_skills(self, skills: List[str]) -> List[str]:
        """
        Clean and deduplicate skills list.
        
        Args:
            skills: List of skills
            
        Returns:
            Cleaned list
        """
        # Remove duplicates (case-insensitive)
        seen = set()
        cleaned = []
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                cleaned.append(skill)
        
        # Sort for consistency
        cleaned.sort()
        
        return cleaned
    
    def categorize_skills(
        self,
        skills: List[str]
    ) -> Dict[str, List[str]]:
        """
        Categorize skills into groups.
        
        Args:
            skills: List of skills
            
        Returns:
            Dictionary mapping categories to skills
        """
        categories = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud_devops': [],
            'tools': [],
            'other': []
        }
        
        for skill in skills:
            categorized = False
            
            for category, patterns in self.SKILL_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, skill, re.IGNORECASE):
                        categories[category].append(skill)
                        categorized = True
                        break
                if categorized:
                    break
            
            if not categorized:
                categories['other'].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}