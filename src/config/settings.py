"""
Configuration management for Adaptive Resume ATS Scorer

"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """
    Centralized configuration management.
    Loads settings from config.yaml and provides type-safe access.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize settings from config file.

        Args:
            config_path: Path to config.yaml. If None, uses default location.
        """
        if config_path is None:
            # Default to project root config.yaml
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
        self._ensure_directories()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

        if not self._config:
            raise ValueError("Configuration file is empty or invalid")

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        paths = self._config.get('paths', {})
        for path_key, path_value in paths.items():
            path = Path(path_value)
            path.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep files to preserve empty directories
            gitkeep = path / '.gitkeep'
            if not gitkeep.exists():
                gitkeep.touch()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'logging.level')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    @property
    def project_name(self) -> str:
        """Get project name."""
        return self.get('project.name', 'Adaptive Resume ATS Scorer')

    @property
    def project_version(self) -> str:
        """Get project version."""
        return self.get('project.version', '0.1.0')

    @property
    def project_phase(self) -> int:
        """Get current evolution phase."""
        return self.get('project.phase', 0)

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get('logging.level', 'INFO')

    @property
    def log_file(self) -> Path:
        """Get log file path."""
        return Path(self.get('logging.log_file', 'data/logs/app.log'))

    @property
    def input_dir(self) -> Path:
        """Get input directory path."""
        return Path(self.get('paths.input_dir', 'data/input'))

    @property
    def output_dir(self) -> Path:
        """Get output directory path."""
        return Path(self.get('paths.output_dir', 'data/output'))

    @property
    def logs_dir(self) -> Path:
        """Get logs directory path."""
        return Path(self.get('paths.logs_dir', 'data/logs'))

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()


# Global settings instance
_settings: Optional[Settings] = None


def get_settings(config_path: Optional[str] = None) -> Settings:
    """
    Get or create global settings instance.

    Args:
        config_path: Path to config file (only used on first call)

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings(config_path)
    return _settings


def reset_settings() -> None:
    """Reset global settings instance. Useful for testing."""
    global _settings
    _settings = None