"""
Unit tests for text vectorizer
"""

import pytest
from src.nlp.text_vectorizer import TextVectorizer


class TestTextVectorizer:
    """Test text vectorization functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.vectorizer = TextVectorizer()
    
    def test_vectorizer_initialization(self):
        """Test vectorizer initializes correctly."""
        assert self.vectorizer is not None
        assert self.vectorizer.vectorizer is not None
    
    def test_extract_keywords_tfidf(self):
        """Test TF-IDF keyword extraction."""
        text = """
        Python developer with experience in machine learning and data science.
        Built REST APIs using Django and Flask frameworks.
        Expertise in SQL databases and data analysis.
        """
        
        keywords = self.vectorizer.extract_keywords_tfidf(text, top_n=10)
        
        assert len(keywords) > 0
        assert all(isinstance(kw, tuple) for kw in keywords)
        assert all(len(kw) == 2 for kw in keywords)
        # Should be sorted by score
        scores = [score for _, score in keywords]
        assert scores == sorted(scores, reverse=True)
    
    def test_extract_keywords_empty_text(self):
        """Test keyword extraction with empty text."""
        keywords = self.vectorizer.extract_keywords_tfidf("", top_n=10)
        assert len(keywords) == 0
    
    def test_calculate_keyword_density(self):
        """Test keyword density calculation."""
        text = "Python developer with Python skills and Python experience"
        keywords = ["Python", "developer"]
        
        density = self.vectorizer.calculate_keyword_density(text, keywords)
        
        assert density > 0
        # "Python" appears 3 times, "developer" 1 time = 4 keywords in 8 words
        # 4/8 * 100 = 50%
        assert 40 < density < 60
    
    def test_detect_keyword_stuffing(self):
        """Test keyword stuffing detection."""
        # Normal text with reasonable keyword usage
        normal_text = """
        Software engineer with 5 years of experience in Python development.
        Strong background in backend systems and API design.
        Worked on multiple projects using modern frameworks.
        """
        keywords = ["Python", "software", "engineer"]
        
        analysis = self.vectorizer.detect_keyword_stuffing(normal_text, keywords)
        
        assert 'density' in analysis
        assert 'is_stuffed' in analysis
        # Should not be flagged as stuffed (only 3 keywords in ~20 words = 15%)
        assert not analysis['is_stuffed']
    
    def test_detect_keyword_stuffing_excessive(self):
        """Test detection of excessive keyword stuffing."""
        # Stuffed text
        stuffed_text = "Python Python Python software software engineer engineer Python Python"
        keywords = ["Python", "software", "engineer"]
        
        analysis = self.vectorizer.detect_keyword_stuffing(stuffed_text, keywords)
        
        assert analysis['is_stuffed']
        assert analysis['density'] > 10  # Very high density
    
    def test_extract_ngrams(self):
        """Test n-gram extraction."""
        text = "machine learning engineer with deep learning experience"
        
        ngrams = self.vectorizer.extract_ngrams(text, n_range=(2, 3))
        
        assert len(ngrams) > 0
        assert "machine learning" in ngrams
        assert "deep learning" in ngrams
    
    def test_calculate_term_frequency(self):
        """Test term frequency calculation."""
        text = "Python developer Python Python skills"
        terms = ["Python", "developer", "Java"]
        
        frequencies = self.vectorizer.calculate_term_frequency(text, terms)
        
        assert frequencies["Python"] == 3
        assert frequencies["developer"] == 1
        assert "Java" not in frequencies
    
    def test_score_keyword_relevance(self):
        """Test keyword relevance scoring."""
        resume_text = """
        Senior Python developer with expertise in machine learning.
        Built scalable REST APIs using Django framework.
        Experience with SQL databases and data analysis.
        """
        
        role_keywords = ["Python", "Django", "machine learning", "API"]
        
        scores = self.vectorizer.score_keyword_relevance(resume_text, role_keywords)
        
        assert len(scores) > 0
        for keyword in role_keywords:
            assert keyword in scores
            assert 0 <= scores[keyword] <= 1