"""
Unit tests for configuration management
Evolution Phase: 0
"""

import pytest
from pathlib import Path

from src.config.settings import Settings, get_settings, reset_settings


class TestSettings:
    """Test Settings class."""

    def test_settings_loads_config(self, sample_config):
        """Test that settings loads configuration correctly."""
        settings = Settings(config_path=sample_config)
        
        assert settings.project_name == "Test ATS Scorer"
        assert settings.project_version == "0.1.0"
        assert settings.project_phase == 0

    def test_settings_creates_directories(self, sample_config, temp_dir):
        """Test that settings creates required directories."""
        settings = Settings(config_path=sample_config)
        
        # Check that directories exist
        assert settings.input_dir.exists()
        assert settings.output_dir.exists()
        assert settings.logs_dir.exists()

    def test_settings_dot_notation_access(self, sample_config):
        """Test dot notation configuration access."""
        settings = Settings(config_path=sample_config)
        
        assert settings.get('project.name') == "Test ATS Scorer"
        assert settings.get('logging.level') == "INFO"
        assert settings.get('environment.encoding') == "utf-8"

    def test_settings_default_values(self, sample_config):
        """Test default value handling."""
        settings = Settings(config_path=sample_config)
        
        # Non-existent key returns default
        assert settings.get('nonexistent.key', 'default') == 'default'
        assert settings.get('another.missing', None) is None

    def test_settings_missing_config_file(self, temp_dir):
        """Test error handling for missing config file."""
        missing_config = temp_dir / "nonexistent.yaml"
        
        with pytest.raises(FileNotFoundError):
            Settings(config_path=missing_config)

    def test_settings_empty_config_file(self, empty_config):
        """Test error handling for empty config file."""
        with pytest.raises(ValueError):
            Settings(config_path=empty_config)

    def test_settings_properties(self, sample_config):
        """Test convenience properties."""
        settings = Settings(config_path=sample_config)
        
        assert settings.project_name == "Test ATS Scorer"
        assert settings.project_version == "0.1.0"
        assert settings.project_phase == 0
        assert settings.log_level == "INFO"
        assert isinstance(settings.log_file, Path)
        assert isinstance(settings.input_dir, Path)

    def test_settings_to_dict(self, sample_config):
        """Test conversion to dictionary."""
        settings = Settings(config_path=sample_config)
        config_dict = settings.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'project' in config_dict
        assert 'logging' in config_dict


class TestGlobalSettings:
    """Test global settings management."""

    def test_get_settings_singleton(self, sample_config):
        """Test that get_settings returns singleton instance."""
        reset_settings()
        
        settings1 = get_settings(config_path=sample_config)
        settings2 = get_settings()
        
        assert settings1 is settings2

    def test_reset_settings(self, sample_config):
        """Test settings reset functionality."""
        settings1 = get_settings(config_path=sample_config)
        reset_settings()
        settings2 = get_settings(config_path=sample_config)
        
        assert settings1 is not settings2