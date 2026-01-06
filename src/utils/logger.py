"""Logging configuration for YouTube SEO Tool.

Provides structured logging with context support for better debugging
and monitoring in production environments.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "youtube_seo",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create formatter
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


# Create module-level loggers
logger = setup_logger("youtube_seo")
api_logger = setup_logger("youtube_seo.api")
cache_logger = setup_logger("youtube_seo.cache")
trends_logger = setup_logger("youtube_seo.trends")


def set_log_level(level: int) -> None:
    """Set log level for all loggers."""
    for log in [logger, api_logger, cache_logger, trends_logger]:
        log.setLevel(level)
        for handler in log.handlers:
            handler.setLevel(level)


def enable_debug() -> None:
    """Enable debug logging."""
    set_log_level(logging.DEBUG)


def disable_logging() -> None:
    """Disable all logging (useful for tests)."""
    set_log_level(logging.CRITICAL + 1)
