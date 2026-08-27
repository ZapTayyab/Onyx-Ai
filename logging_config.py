"""Structured logging setup used by the application and services."""

from __future__ import annotations

import logging
from logging.config import dictConfig

from config import get_config


def configure_logging() -> None:
    """Configure standard JSON-like console logging for all environments."""
    config = get_config()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s | %(levelname)s | %(name)s | "
                        "%(message)s"
                    )
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": config.log_level,
                }
            },
            "root": {"handlers": ["console"], "level": config.log_level},
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module logger."""
    return logging.getLogger(name)
