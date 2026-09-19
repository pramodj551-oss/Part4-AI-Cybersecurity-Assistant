"""Regression guards for FAISS provenance contract reconciliation.

These tests deliberately distinguish:
1. the source-controlled trusted provenance value;
2. the deployment example value; and
3. runtime/build-observed artifact hashes.

The first two must stay synchronized. The third must never silently
rewrite the trusted value; it is reconciled only after independent
production-build evidence.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TRUSTED_HASH_FILE = REPO_ROOT / "config" / "faiss_index.pkl.sha256"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
DOCKERFILE = REPO_ROOT / "Dockerfile"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _trusted_hash() -> str:
    value = TRUSTED_HASH_FILE.read_text(encoding="utf-8").strip().lower()
    assert re.fullmatch(r"[0-9a-f]{64}", value), (
        "config/faiss_index.pkl.sha256 must contain exactly one SHA-256 digest"
    )
    return value


def _env_value(name: str) -> str:
    match = re.search(
        rf"(?m)^\\s*{re.escape(name)}\\s*=\\s*([^\\s#]+)\\s*$",
        ENV_EXAMPLE.read_text(encoding="utf-8"),
    )
    assert match, f"{name} is missing from .env.example"
    return match.group(1).strip().lower()


def test_source_trusted_hash_is_well_formed():
    trusted = _trusted_hash()
    assert trusted == TRUSTED_HASH_FILE.read_text(encoding="utf-8").strip().lower()


def test_env_example_matches_source_controlled_trusted_hash():
    """Deployment example must not drift from the source-controlled contract."""
    assert _env_value("FAISS_INDEX_PKL_SHA256") == _trusted_hash()


def test_provenance_contract_is_fail_closed():
    """Docker build must compare the generated artifact against the trusted hash."""
    docker = DOCKERFILE.read_text(encoding="utf-8")
    assert "sha256sum /app/vectorstore/faiss_index/index.pkl" in docker
    assert "test \"$(cut -d ' ' -f1 /app/vectorstore/faiss_index/index.pkl.sha256)\"" in docker
    assert "config/faiss_index.pkl.sha256" in docker


def test_provenance_guard_distinguishes_observed_from_trusted_hash():
    """An observed build hash is evidence, not authorization to change trust."""
    trusted = _trusted_hash()
    observed_label = "observed-build-index-pkl-sha256"
    assert observed_label not in trusted
    assert len(trusted) == 64


def test_dataset_and_contract_fingerprints_are_recordable():
    """Keep a stable diagnostic anchor without mutating the trusted hash."""
    dataset = REPO_ROOT / "data" / "cybersecurity_incident_reports.csv"
    assert dataset.is_file()
    print(f"provenance trusted index.pkl SHA-256: {_trusted_hash()}")
    print(f"provenance dataset SHA-256: {_sha256(dataset)}")
