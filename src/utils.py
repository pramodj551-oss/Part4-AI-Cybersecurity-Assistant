"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Utility Functions
Version: 4.0
==========================================================
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path


def setup_logger(
    name: str,
    log_file: str | Path,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configure and return a logger.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_file = Path(log_file)
    log_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def ensure_directory(path: str | Path) -> Path:
    """
    Create a directory if it does not exist.
    """

    path = Path(path)

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    return path


def validate_file(file_path: str | Path) -> bool:
    """
    Validate file existence.
    """

    return Path(file_path).exists()


def clean_text(text: str) -> str:
    """
    Basic text normalization.
    """

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def remove_duplicate_strings(
    values: list[str]
) -> list[str]:
    """
    Remove duplicate strings while
    preserving order.
    """

    seen = set()

    result = []

    for value in values:

        if value not in seen:

            seen.add(value)

            result.append(value)

    return result


def timestamp() -> str:
    """
    Current timestamp.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def file_size_mb(
    file_path: str | Path
) -> float:
    """
    File size in MB.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        return 0.0

    return round(
        file_path.stat().st_size / (1024 * 1024),
        2
    )


def supported_document(
    file_path: str | Path
) -> bool:
    """
    Check supported document format.
    """

    supported = {
        ".pdf",
        ".txt",
        ".md",
        ".csv"
    }

    return (
        Path(file_path)
        .suffix
        .lower()
        in supported
  )
