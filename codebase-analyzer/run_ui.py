#!/usr/bin/env python3
"""
Main entry point for the Codebase Analyzer UI application.

Usage:
    python run_ui.py
"""

import sys
from pathlib import Path

# Add project root to path so 'src' is importable as a package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.app import run_app
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main entry point."""
    try:
        # Load configuration
        config = Config()
        
        logger.info("Starting Codebase Analyzer UI...")
        
        # Run the application
        run_app(config)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
