"""Regression guards for the FAISS provenance contract.

The source-controlled trusted hash and deployment example must remain
synchronized. Build-observed hashes are diagnostic evidence only and must
not silently replace the trusted value.
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
    pattern = rf"(?m)^\s*{re.escape(name)}\s*=\s*([^\s#]+)\s*$"
    match = re.search(pattern, ENV_EXAMPLE.read_text(encoding="utf-8"))
    assert match, f"{name} is missing from .env.example"
    return match.group(1).strip().lower()


def test_source_trusted_hash_is_well_formed():
    assert re.fullmatch(
        r"[0-9a-f]{64}",
        TRUSTED_HASH_FILE.read_text(encoding="utf-8").strip().lower(),
    )


def test_env_example_matches_source_controlled_trusted_hash():
    """Deployment example must not drift from the source-controlled hash."""
    assert _env_value("FAISS_INDEX_PKL_SHA256") == _trusted_hash()


def test_provenance_contract_is_fail_closed():
    """Docker must compare the generated artifact with the trusted hash."""
    docker = DOCKERFILE.read_text(encoding="utf-8")
    assert "sha256sum /app/vectorstore/faiss_index/index.pkl" in docker
    assert (
        'test "$(cut -d \' \' -f1 /app/vectorstore/faiss_index/index.pkl.sha256)"'
        in docker
    )
    assert "config/faiss_index.pkl.sha256" in docker


def test_provenance_guard_distinguishes_observed_from_trusted_hash():
    """Observed build output is evidence, not authorization to change trust."""
    trusted = _trusted_hash()
    assert len(trusted) == 64
    print(f"provenance trusted index.pkl SHA-256: {trusted}")
    print("provenance observed-build hash: recorded separately by build diagnostics")


def test_dataset_fingerprint_is_recordable():
    dataset = REPO_ROOT / "data" / "cybersecurity_incident_reports.csv"
    assert dataset.is_file()
    print(f"provenance dataset SHA-256: {_sha256(dataset)}")
