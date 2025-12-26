"""
Custom exceptions for Adaptive Resume ATS Scorer

"""


class ATSScorerException(Exception):
    """Base exception for ATS Scorer application."""
    pass


class ConfigurationError(ATSScorerException):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(ATSScorerException):
    """Raised when validation fails."""
    pass


class PipelineError(ATSScorerException):
    """Raised when pipeline execution fails."""
    pass


