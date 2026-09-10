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


_SENSITIVE_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;]+"),
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)(bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)(password\s*[:=]\s*)[^\s,;]+"),
    re.compile(r"(?i)(secret\s*[:=]\s*)[^\s,;]+"),
    re.compile(r"(?i)(token\s*[:=]\s*)[^\s,;]+"),
)


def redact_sensitive_data(message: object) -> str:
    """Return a log-safe representation with common credential values redacted."""
    text = str(message)
    for pattern in _SENSITIVE_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    return text


class PrivacyRedactionFilter(logging.Filter):
    """Redact credential-like values before records reach any configured handler."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_sensitive_data(record.getMessage())
        record.args = ()
        return True


def audit_event(logger: logging.Logger, event: str, **fields: object) -> None:
    """Emit a privacy-safe structured audit event without logging field values raw."""
    safe_fields = " ".join(
        f"{key}={redact_sensitive_data(value)}"
        for key, value in sorted(fields.items())
    )
    logger.info("audit_event=%s %s", redact_sensitive_data(event), safe_fields)


def setup_logger(
    name: str,
    log_file: str | Path,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configure and return a privacy-safe logger.
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

    privacy_filter = PrivacyRedactionFilter()

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(privacy_filter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(privacy_filter)

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
