"""
Unit tests for Hello Pipeline
Evolution Phase: 0
"""

import pytest
from pathlib import Path
import shutil

from src.pipeline.hello_pipeline import HelloPipeline
from src.config.settings import Settings
from src.utils.exceptions import PipelineError


class TestHelloPipeline:
    """Test Hello Pipeline functionality."""

    def test_pipeline_initialization(self, sample_config):
        """Test pipeline initializes correctly."""
        Settings(config_path=sample_config)
        pipeline = HelloPipeline()
        
        assert pipeline.logger is not None
        assert pipeline.settings is not None

    def test_verify_python_version(self, sample_config):
        """Test Python version verification."""
        Settings(config_path=sample_config)
        pipeline = HelloPipeline()
        
        result = pipeline.verify_python_version()
        assert result is True  # Should pass on Python 3.9+

    def test_verify_directories(self, sample_config):
        """Test directory verification."""
        Settings(config_path=sample_config)
        pipeline = HelloPipeline()
        
        result = pipeline.verify_directories()
        assert result is True

    def test_verify_configuration(self, sample_config):
        """Test configuration verification."""
        Settings(config_path=sample_config)
        pipeline = HelloPipeline()
        
        result = pipeline.verify_configuration()
        assert result is True

    def test_verify_logging(self, sample_config):
        """Test logging verification."""
        Settings(config_path=sample_config)
        pipeline = HelloPipeline()
        
        result = pipeline.verify_logging()
        assert result is True

    def test_pipeline_run_success(self, sample_config):
        """Test successful pipeline run."""
        Settings(config_path=sample_config)
        pipeline = HelloPipeline()
        
        results = pipeline.run()
        
        assert isinstance(results, dict)
        assert 'python_version' in results
        assert 'directories' in results
        assert 'configuration' in results
        assert 'logging' in results
        assert 'all_passed' in results
        assert results['all_passed'] is True

    def test_pipeline_results_structure(self, sample_config):
        """Test pipeline results have correct structure."""
        Settings(config_path=sample_config)
        pipeline = HelloPipeline()
        
        results = pipeline.run()
        
        # All verification results should be boolean
        for key, value in results.items():
            assert isinstance(value, bool)

    def test_pipeline_creates_log_file(self, sample_config):
        """Test that pipeline creates log file."""
        settings = Settings(config_path=sample_config)
        pipeline = HelloPipeline()
        pipeline.run()
        
        # Ensure logger handlers flush
        for handler in pipeline.logger.handlers:
            handler.flush()
        
        # Check that the actual log file exists (app.log, not test.log)
        # The pipeline logs to the configured log file
        actual_log_file = Path('data/logs/app.log')
        assert actual_log_file.exists(), "Log file should be created at data/logs/app.log"

    def test_pipeline_handles_missing_directory_gracefully(self, sample_config):
        """Test pipeline behavior with missing directories."""
        settings = Settings(config_path=sample_config)
        pipeline = HelloPipeline()
        
        # Remove a directory AFTER pipeline initialization
        # to test the verify_directories method's detection capability
        test_dir = settings.input_dir
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        # Now verify_directories should detect it's missing
        result = pipeline.verify_directories()
        
        # Should detect missing directory
        assert result is False, "verify_directories should return False when directory is missing"