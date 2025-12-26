"""
Pytest configuration and fixtures
Evolution Phase: 0
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator

from src.config.settings import reset_settings


@pytest.fixture(autouse=True)
def reset_global_settings():
    """Reset global settings before each test."""
    reset_settings()
    yield
    reset_settings()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for testing.

    Yields:
        Path to temporary directory
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_config(temp_dir: Path) -> Path:
    """
    Create a sample configuration file for testing.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path to sample config file
    """
    config_content = """
project:
  name: "Test ATS Scorer"
  version: "0.1.0"
  phase: 0

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_enabled: true
  console_enabled: true
  log_file: "data/logs/test.log"
  max_bytes: 1048576
  backup_count: 3

paths:
  data_root: "data"
  input_dir: "data/input"
  output_dir: "data/output"
  logs_dir: "data/logs"

environment:
  python_version: "3.9+"
  encoding: "utf-8"
  timezone: "UTC"
"""
    
    config_file = temp_dir / "test_config.yaml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def empty_config(temp_dir: Path) -> Path:
    """
    Create an empty configuration file for testing error handling.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path to empty config file
    """
    config_file = temp_dir / "empty_config.yaml"
    config_file.write_text("")
    return config_file