"""Logging configuration for the Codebase Analyzer application."""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from .config import get_config


def setup_logger(log_file: Optional[Path] = None) -> None:
    """
    Configure application logging.

    Args:
        log_file: Optional path to log file. If None, uses default location.
    """
    # Remove default handler
    logger.remove()

    # Get configuration
    config = get_config()
    log_level = config.log_level

    # Console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # File handler
    if log_file is None:
        project_root = Path(__file__).parent.parent.parent
        log_file = project_root / "logs" / "analyzer.log"

    # Create logs directory if it doesn't exist
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    logger.info(f"Logger initialized with level: {log_level}")
    logger.info(f"Log file: {log_file}")


def get_logger(name: str):
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name

    Returns:
        Logger instance
    """
    return logger.bind(name=name)

# Made with Bob
