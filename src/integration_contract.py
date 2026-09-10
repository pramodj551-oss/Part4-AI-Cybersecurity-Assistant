"""Validate the Part 3 -> Part 4 runtime artifact handoff contract.

Part 3 is a consumer/presentation layer over the pinned Part 2 runtime bundle.
Part 4 does not copy or execute those model artifacts. This module validates a
handoff manifest supplied by deployment/integration tooling so provenance and
artifact identity are explicit and fail closed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PART3_REPOSITORY = "pramodj551-oss/Part3-Cybersecurity-Dashboard"
PART2_REPOSITORY = "pramodj551-oss/Part2-Cybersecurity-ML-Pipeline"
EXPECTED_ARTIFACTS = (
    "models/best_model.pkl",
    "models/preprocessor.pkl",
    "models/feature_columns.pkl",
    "outputs/evaluation_report.json",
    "outputs/metrics.json",
    "outputs/feature_importance.csv",
)
_REQUIRED_FIELDS = {
    "source_repository",
    "source_release_tag",
    "source_release_commit",
    "bundle_name",
    "bundle_sha256",
    "files",
}
_HEX64 = set("0123456789abcdef")


class IntegrationContractError(ValueError):
    """Raised when the external handoff contract is invalid."""


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value.lower()) <= _HEX64


def load_handoff_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    if not manifest_path.is_file() or manifest_path.stat().st_size == 0:
        raise IntegrationContractError("handoff manifest missing or empty")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrationContractError("handoff manifest is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise IntegrationContractError("handoff manifest must be a JSON object")
    return payload


def validate_handoff_manifest(
    manifest: dict[str, Any],
    *,
    expected_part3_repository: str = PART3_REPOSITORY,
    expected_part2_repository: str = PART2_REPOSITORY,
) -> bool:
    """Validate provenance and exact artifact schema without touching artifacts."""
    if set(manifest) != _REQUIRED_FIELDS:
        raise IntegrationContractError("manifest fields do not match the required schema")
    if manifest["source_repository"] != expected_part2_repository:
        raise IntegrationContractError("source repository provenance mismatch")
    if not isinstance(manifest["source_release_tag"], str) or not manifest["source_release_tag"]:
        raise IntegrationContractError("source release tag is required")
    if not _is_sha256(manifest["source_release_commit"]):
        raise IntegrationContractError("source release commit must be a SHA-256-length hex value")
    if not isinstance(manifest["bundle_name"], str) or not manifest["bundle_name"]:
        raise IntegrationContractError("bundle name is required")
    if not _is_sha256(manifest["bundle_sha256"]):
        raise IntegrationContractError("bundle SHA-256 is invalid")

    files = manifest["files"]
    if not isinstance(files, dict) or tuple(files) != EXPECTED_ARTIFACTS:
        raise IntegrationContractError("artifact manifest must contain exactly the six Part 3 runtime artifacts")
    if any(not _is_sha256(value) for value in files.values()):
        raise IntegrationContractError("artifact SHA-256 values are invalid")

    # Keep the Part 3 identity explicit at the validation boundary. The
    # manifest's source_repository remains the pinned Part 2 producer because
    # Part 3's own manifest is a declaration of the Part 2 runtime bundle.
    if expected_part3_repository != PART3_REPOSITORY:
        raise IntegrationContractError("unsupported Part 3 repository contract")
    return True


def validate_artifacts_against_manifest(
    artifact_root: str | Path, manifest: dict[str, Any]
) -> bool:
    """Fail closed when any declared artifact is missing, empty, or tampered."""
    validate_handoff_manifest(manifest)
    root = Path(artifact_root)
    for relative_path in EXPECTED_ARTIFACTS:
        path = root / relative_path
        if not path.is_file() or path.stat().st_size == 0:
            raise IntegrationContractError(f"artifact missing or empty: {relative_path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != manifest["files"][relative_path]:
            raise IntegrationContractError(f"artifact checksum mismatch: {relative_path}")
    return True
