"""
Hello Pipeline - Environment Verification
Evolution Phase: 0
"""

import sys
from pathlib import Path
from typing import Dict, Any

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.exceptions import PipelineError


class HelloPipeline:
    """
    Simple pipeline to verify environment setup.
    Tests configuration loading, logging, and basic functionality.
    """

    def __init__(self):
        """Initialize Hello Pipeline."""
        self.logger = get_logger(__name__)
        self.settings = get_settings()
        self.logger.info("Hello Pipeline initialized")

    def verify_python_version(self) -> bool:
        """
        Verify Python version meets requirements.

        Returns:
            True if version is acceptable
        """
        version_info = sys.version_info
        if version_info.major >= 3 and version_info.minor >= 9:
            self.logger.info(
                f"Python version {version_info.major}.{version_info.minor}.{version_info.micro} OK"
            )
            return True
        else:
            self.logger.error(
                f"Python version {version_info.major}.{version_info.minor} is too old. "
                "Requires 3.9+"
            )
            return False

    def verify_directories(self) -> bool:
        """
        Verify all required directories exist.

        Returns:
            True if all directories exist
        """
        required_dirs = [
            self.settings.input_dir,
            self.settings.output_dir,
            self.settings.logs_dir,
        ]

        all_exist = True
        for directory in required_dirs:
            if directory.exists():
                self.logger.debug(f"Directory exists: {directory}")
            else:
                self.logger.error(f"Directory missing: {directory}")
                all_exist = False

        if all_exist:
            self.logger.info("All required directories verified")

        return all_exist

    def verify_configuration(self) -> bool:
        """
        Verify configuration is loaded and valid.

        Returns:
            True if configuration is valid
        """
        try:
            # Test configuration access
            project_name = self.settings.project_name
            version = self.settings.project_version
            phase = self.settings.project_phase

            self.logger.info(
                f"Configuration loaded: {project_name} v{version} (Phase {phase})"
            )

            # Verify key configuration values
            if not project_name:
                raise ValueError("Project name is empty")
            if phase != 0:
                self.logger.warning(f"Expected phase 0, got phase {phase}")

            return True

        except Exception as e:
            self.logger.error(f"Configuration verification failed: {e}")
            return False

    def verify_logging(self) -> bool:
        """
        Verify logging system works.

        Returns:
            True if logging works
        """
        try:
            # Test different log levels
            self.logger.debug("Debug message test")
            self.logger.info("Info message test")
            self.logger.warning("Warning message test")

            # Verify log file creation
            log_file = self.settings.log_file
            if log_file.exists():
                self.logger.info(f"Log file created: {log_file}")
                return True
            else:
                self.logger.error(f"Log file not created: {log_file}")
                return False

        except Exception as e:
            self.logger.error(f"Logging verification failed: {e}")
            return False

    def run(self) -> Dict[str, Any]:
        """
        Run hello pipeline verification.

        Returns:
            Dictionary containing verification results

        Raises:
            PipelineError: If critical verification fails
        """
        self.logger.info("Starting environment verification")

        results = {
            "python_version": self.verify_python_version(),
            "directories": self.verify_directories(),
            "configuration": self.verify_configuration(),
            "logging": self.verify_logging(),
        }

        # Calculate overall status
        results["all_passed"] = all(results.values())

        if results["all_passed"]:
            self.logger.info("✓ Environment verification: PASSED")
            self.logger.info("✓ Configuration loaded successfully")
            self.logger.info("✓ Logger functioning correctly")
            self.logger.info("✓ Hello Pipeline completed successfully")
        else:
            failed_checks = [k for k, v in results.items() if not v and k != "all_passed"]
            self.logger.error(f"✗ Environment verification: FAILED - {failed_checks}")
            raise PipelineError(f"Verification failed: {failed_checks}")

        return results


def main():
    """Entry point for hello pipeline."""
    try:
        pipeline = HelloPipeline()
        results = pipeline.run()
        
        # Print results
        print("\n" + "="*60)
        print("HELLO PIPELINE - ENVIRONMENT VERIFICATION")
        print("="*60)
        for check, passed in results.items():
            if check != "all_passed":
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"{check.upper()}: {status}")
        print("="*60)
        print(f"OVERALL: {'✓ PASSED' if results['all_passed'] else '✗ FAILED'}")
        print("="*60 + "\n")

        return 0 if results["all_passed"] else 1

    except Exception as e:
        print(f"✗ Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())