"""Structured logging setup."""

import logging
import sys

import structlog
from structlog.types import Processor

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Install structlog as the single logging facade.

    Console output is human-readable in development and line-delimited JSON in
    production so logs can be shipped without extra parsing.
    """
    level = logging.getLevelNamesMapping()[settings.log_level]

    renderer: Processor
    if settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
