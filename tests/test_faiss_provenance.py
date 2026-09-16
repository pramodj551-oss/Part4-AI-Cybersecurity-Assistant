"""Regression tests for the immutable FAISS artifact provenance contract."""

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
TRUSTED_HASH_PATH = REPO_ROOT / "config" / "faiss_index.pkl.sha256"
ENV_EXAMPLE_PATH = REPO_ROOT / ".env.example"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _trusted_hash() -> str:
    return TRUSTED_HASH_PATH.read_text(encoding="utf-8").strip().lower()


def _example_faiss_hash() -> str:
    for line in ENV_EXAMPLE_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("FAISS_INDEX_PKL_SHA256="):
            return line.split("=", 1)[1].strip().lower()
    raise AssertionError("FAISS_INDEX_PKL_SHA256 is missing from .env.example")


def test_trusted_faiss_hash_is_valid_sha256():
    assert SHA256_RE.fullmatch(_trusted_hash())


def test_env_example_matches_source_controlled_faiss_contract():
    assert _example_faiss_hash() == _trusted_hash()


def test_dockerfile_enforces_trusted_faiss_hash_at_build_time():
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "config/faiss_index.pkl.sha256" in dockerfile
    assert "sha256sum /app/vectorstore/faiss_index/index.pkl" in dockerfile
    assert "refusing deserialization" not in dockerfile
