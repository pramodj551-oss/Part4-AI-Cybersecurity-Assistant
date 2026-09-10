"""Container health/readiness checks for the Streamlit application."""

from __future__ import annotations

import argparse
import os
import sys
from urllib.error import URLError
from urllib.request import urlopen


def _streamlit_health(port: int) -> bool:
    """Return True when Streamlit's native health endpoint responds successfully."""
    try:
        with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=3) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


def check_health(port: int) -> bool:
    return _streamlit_health(port)


def check_readiness(port: int) -> bool:
    """Check serving health and fail closed for invalid production configuration."""
    if not _streamlit_health(port):
        return False

    if os.getenv("APP_ENVIRONMENT", "development").strip().lower() in {"production", "prod"}:
        try:
            from config.config import validate_production_config

            validate_production_config()
        except Exception:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--health", action="store_true")
    group.add_argument("--ready", action="store_true")
    parser.add_argument("--port", type=int, default=8502)
    args = parser.parse_args()

    ok = check_health(args.port) if args.health else check_readiness(args.port)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
