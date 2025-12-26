"""
Text processing utilities
"""

import re
from typing import List, Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove null bytes and other problematic characters
    text = text.replace('\x00', '')
    
    # Normalize whitespace
    text = re.sub(r'\r\n', '\n', text)  # Normalize line endings
    text = re.sub(r'\r', '\n', text)
    
    # Remove excessive blank lines (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove trailing/leading whitespace from lines
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def extract_email(text: str) -> Optional[str]:
    """
    Extract email address from text.
    
    Args:
        text: Text to search
        
    Returns:
        First email found or None
    """
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    """
    Extract phone number from text.
    
    Args:
        text: Text to search
        
    Returns:
        First phone number found or None
    """
    # Match various phone formats
    patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-234-567-8900
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (234) 567-8900
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # 234-567-8900
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    
    return None


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of URLs found
    """
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, text)


def extract_linkedin(text: str) -> Optional[str]:
    """
    Extract LinkedIn URL from text.
    
    Args:
        text: Text to search
        
    Returns:
        LinkedIn URL or None
    """
    pattern = r'https?://(?:www\.)?linkedin\.com/in/[^\s]+'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


def extract_github(text: str) -> Optional[str]:
    """
    Extract GitHub URL from text.
    
    Args:
        text: Text to search
        
    Returns:
        GitHub URL or None
    """
    pattern = r'https?://(?:www\.)?github\.com/[^\s]+'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count
        
    Returns:
        Number of words
    """
    if text=="":
        return 1
    return len(text.split())


def normalize_section_name(name: str) -> str:
    """
    Normalize section name for consistent matching.
    
    Args:
        name: Section name to normalize
        
    Returns:
        Normalized name (lowercase, no special chars)
    """
    # Convert to lowercase
    name = name.lower()
    
    # Remove special characters except spaces
    name = re.sub(r'[^a-z\s]', '', name)
    
    # Replace multiple spaces with single space
    name = re.sub(r'\s+', ' ', name)
    
    return name.strip()


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting (can be improved)
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def remove_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace from text.
    
    Args:
        text: Text to process
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n+', '\n\n', text)
    
    return text.strip()