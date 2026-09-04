#!/usr/bin/env python3
"""Optional synchronizer for the Part 1 companion repository.

Part 4 consumes the incident-report dataset as its authoritative RAG input.
The source contract is Part 1 ``data/raw/cybersecurity_incident_reports.csv``
to Part 4 ``data/cybersecurity_incident_reports.csv``. Part 2 model artifacts
and Part 3 config/theme files are intentionally not copied here; Part 4 does
not consume those artifacts directly. Every copied file is verified with
SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("sync_repos")


class RepositorySynchronizer:
    def __init__(self, part4_path: str = ".", part1_path: str | None = None,
                 part2_path: str | None = None, part3_path: str | None = None):
        self.part4_path = Path(part4_path).resolve()
        self.part1_path = Path(part1_path).resolve() if part1_path else None
        # Kept for CLI compatibility; Part 2/3 artifacts are not part of the
        # Part 4 runtime contract and must not be copied into this repository.
        self.part2_path = Path(part2_path).resolve() if part2_path else None
        self.part3_path = Path(part3_path).resolve() if part3_path else None
        self.sync_log = {
            "timestamp": datetime.now().isoformat(),
            "synced_files": [],
            "skipped": [],
            "errors": [],
        }

    @staticmethod
    def checksum(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def copy_file(self, source: Path, destination: Path) -> bool:
        if not source.is_file():
            self.sync_log["errors"].append(f"Required source missing: {source}")
            logger.error("Required source missing: %s", source)
            return False
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            expected = self.checksum(source)
            shutil.copy2(source, destination)
            actual = self.checksum(destination)
            if expected != actual:
                raise RuntimeError(f"Checksum mismatch after copying {source}")
            self.sync_log["synced_files"].append({
                "source": str(source),
                "destination": str(destination),
                "sha256": actual,
            })
            return True
        except Exception as error:
            logger.exception("Sync failed for %s", source)
            self.sync_log["errors"].append(str(error))
            return False

    def sync_part1_data(self) -> bool:
        if not self.part1_path:
            self.sync_log["skipped"].append("Part 1: path not configured")
            return True

        source = self.part1_path / "data" / "raw" / "cybersecurity_incident_reports.csv"
        destination = self.part4_path / "data" / "cybersecurity_incident_reports.csv"
        return self.copy_file(source, destination)

    def validate(self) -> bool:
        dataset = self.part4_path / "data" / "cybersecurity_incident_reports.csv"
        if not dataset.is_file() or dataset.stat().st_size == 0:
            self.sync_log["errors"].append(f"Authoritative dataset missing or empty: {dataset}")
            return False
        return not self.sync_log["errors"]

    def save_log(self) -> None:
        path = self.part4_path / "sync_repos.log.json"
        path.write_text(json.dumps(self.sync_log, indent=2), encoding="utf-8")

    def sync_all(self) -> bool:
        result = self.sync_part1_data()
        result = self.validate() and result
        self.save_log()
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--part1-path")
    # Retain these arguments so existing automation does not break while the
    # obsolete Part 2/3 copy contract is removed.
    parser.add_argument("--part2-path")
    parser.add_argument("--part3-path")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    synchronizer = RepositorySynchronizer(
        part1_path=args.part1_path,
        part2_path=args.part2_path,
        part3_path=args.part3_path,
    )
    raise SystemExit(0 if synchronizer.sync_all() else 1)
