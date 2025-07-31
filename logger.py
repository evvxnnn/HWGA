"""
Logging utility for the Security Ops Logger application.

This module centralizes logging configuration so that all parts
of the application can easily obtain a configured logger. By
default logs are written to a file in the ``logs`` directory
relative to the project root. Each logger is set up with a
consistent format and log level. If the log directory does not
exist it will be created automatically.

Example usage:

    from logger import get_logger

    logger = get_logger(__name__)
    logger.info("Starting application")

The same logger instance will be returned for subsequent calls
with the same name. Handlers are only added once to avoid
duplicate log messages.
"""

import logging
import os
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger with the given name.

    If the logger has not been configured previously, this
    function will create a ``logs`` directory (if necessary), add
    a ``FileHandler`` writing to ``logs/app.log``, and apply a
    standard log format. The log level defaults to ``INFO``.

    Parameters
    ----------
    name: str or None
        The name of the logger to return. If ``None`` then the
        root logger is returned.

    Returns
    -------
    logging.Logger
        A configured logger instance.
    """

    logger = logging.getLogger(name)

    # Avoid adding multiple handlers to the same logger
    if not logger.handlers:
        # Ensure the logs directory exists
        log_dir = "logs"
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception:
            # In case logs directory cannot be created, fallback to current
            log_dir = "."

        log_file = os.path.join(log_dir, "app.log")
        handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Default level is INFO; modules can override after retrieving
        logger.setLevel(logging.INFO)

    return logger