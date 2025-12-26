"""
Logging utilities for Adaptive Resume ATS Scorer
Evolution Phase: 0
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler

from src.config.settings import get_settings


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    console: bool = True,
    file_logging: bool = True
) -> logging.Logger:
    """
    Set up logger with console and file handlers.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        console: Enable console logging
        file_logging: Enable file logging

    Returns:
        Configured logger instance
    """
    settings = get_settings()

    # Get configuration
    if level is None:
        level = settings.log_level
    if log_file is None:
        log_file = settings.log_file

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    log_format = settings.get(
        'logging.format',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    formatter = logging.Formatter(log_format)

    # Console handler
    if console and settings.get('logging.console_enabled', True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if file_logging and settings.get('logging.file_enabled', True):
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        max_bytes = settings.get('logging.max_bytes', 10485760)  # 10MB
        backup_count = settings.get('logging.backup_count', 5)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with standard configuration.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    # Check if logger already exists and is configured
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    # Configure new logger
    return setup_logger(name)