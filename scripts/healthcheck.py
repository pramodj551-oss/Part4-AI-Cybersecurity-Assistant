"""Container health and readiness checks for the Streamlit service."""

from __future__ import annotations

import argparse
import os
from urllib.error import URLError
from urllib.request import urlopen


def _streamlit_health(port: int) -> bool:
    """Return True only when Streamlit's native health endpoint is healthy."""
    try:
        with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=3) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


def check_health(port: int = 8502) -> bool:
    """Check the application's serving process."""
    return _streamlit_health(port)


def check_readiness(port: int = 8502) -> bool:
    """Check serving health plus required startup dependencies/configuration."""
    if not check_health(port):
        return False

    try:
        from src.startup import check_startup

        if not check_startup():
            return False
    except Exception:
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
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--health", action="store_true")
    mode.add_argument("--ready", action="store_true")
    parser.add_argument("--port", type=int, default=8502)
    args = parser.parse_args()

    ok = check_health(args.port) if args.health else check_readiness(args.port)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
