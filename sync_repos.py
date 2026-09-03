#!/usr/bin/env python3
"""Optional synchronizer for the Part 1/2/3 companion repositories.

A fresh Part 4 checkout must remain usable without sibling repositories. Missing
companion artifacts are reported as skipped rather than silently copied into
incorrect paths. Every copied file is verified with SHA-256.
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
        self.part2_path = Path(part2_path).resolve() if part2_path else None
        self.part3_path = Path(part3_path).resolve() if part3_path else None
        self.sync_log = {"timestamp": datetime.now().isoformat(), "synced_files": [], "skipped": [], "errors": []}

    @staticmethod
    def checksum(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def copy_file(self, source: Path, destination: Path) -> bool:
        if not source.is_file():
            self.sync_log["skipped"].append(str(source))
            logger.warning("Skipped missing source: %s", source)
            return True
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            expected = self.checksum(source)
            shutil.copy2(source, destination)
            actual = self.checksum(destination)
            if expected != actual:
                raise RuntimeError(f"Checksum mismatch after copying {source}")
            self.sync_log["synced_files"].append({"source": str(source), "destination": str(destination), "sha256": actual})
            return True
        except Exception as error:
            logger.exception("Sync failed for %s", source)
            self.sync_log["errors"].append(str(error))
            return False

    def sync_part1_data(self) -> bool:
        if not self.part1_path:
            self.sync_log["skipped"].append("Part 1: path not configured")
            return True
        mapping = {
            "cybersecurity_incidents.csv": "data/cybersecurity_incident_reports.csv",
            "cybersecurity_incident_reports.csv": "data/cybersecurity_incident_reports.csv",
            "kpi_metrics.json": "data/kpi_metrics.json",
            "security_events.csv": "data/security_events.csv",
            "alerts.json": "data/alerts.json",
        }
        ok = True
        for name, destination in mapping.items():
            ok = self.copy_file(self.part1_path / "data" / name, self.part4_path / destination) and ok
        for directory in ("sop_documents", "knowledge_base"):
            source = self.part1_path / "data" / directory
            if not source.is_dir():
                self.sync_log["skipped"].append(str(source))
                continue
            target = self.part4_path / "data" / directory
            target.mkdir(parents=True, exist_ok=True)
            for file in source.rglob("*"):
                if file.is_file():
                    ok = self.copy_file(file, target / file.relative_to(source)) and ok
        return ok

    def sync_part2_models(self) -> bool:
        if not self.part2_path:
            self.sync_log["skipped"].append("Part 2: path not configured")
            return True
        ok = True
        for file in ("trained_model.pkl", "feature_scaler.pkl", "label_encoder.pkl", "preprocessing_pipeline.pkl",
                     "feature_names.json", "model_metrics.json", "class_labels.json", "hyperparameters.json"):
            ok = self.copy_file(self.part2_path / "models" / file, self.part4_path / "models" / file) and ok
        ok = self.copy_file(self.part2_path / "data" / "predictions.csv", self.part4_path / "data" / "predictions.csv") and ok
        return ok

    def sync_part3_config(self) -> bool:
        if not self.part3_path:
            self.sync_log["skipped"].append("Part 3: path not configured")
            return True
        ok = True
        for file in ("config.py", "theme.json"):
            ok = self.copy_file(self.part3_path / "config" / file, self.part4_path / "config" / f"config_part3.{file.split('.')[-1]}") and ok
        return ok

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
        results = [self.sync_part1_data(), self.sync_part2_models(), self.sync_part3_config(), self.validate()]
        self.save_log()
        return all(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--part1-path")
    parser.add_argument("--part2-path")
    parser.add_argument("--part3-path")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    synchronizer = RepositorySynchronizer(part1_path=args.part1_path, part2_path=args.part2_path, part3_path=args.part3_path)
    raise SystemExit(0 if synchronizer.sync_all() else 1)
