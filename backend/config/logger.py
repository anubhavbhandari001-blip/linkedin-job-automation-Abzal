"""
Shared logging configuration.

Replaces the scattered print() calls with real logging: timestamped,
leveled, and persisted to logs/automation.log so a headless or failed
run can still be diagnosed after the fact.

Usage:
    from config.logger import get_logger
    log = get_logger(__name__)
    log.info("Starting search...")
"""

import logging
from logging.handlers import RotatingFileHandler

from config.settings import LOG_FILE, LOG_LEVEL

_CONFIGURED = False


def _configure_root_logger():
    global _CONFIGURED

    if _CONFIGURED:
        return

    root = logging.getLogger("linkedin_automation")
    root.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    root.propagate = False

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    _configure_root_logger()
    return logging.getLogger(f"linkedin_automation.{name}")
