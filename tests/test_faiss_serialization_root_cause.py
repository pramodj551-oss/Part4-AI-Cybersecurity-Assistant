"""Root-cause diagnostics for FAISS artifact serialization determinism."""

from __future__ import annotations

import hashlib
import pickle
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class DeterministicEmbeddings(Embeddings):
    """Dependency-free deterministic embeddings for byte-level diagnostics."""

    @staticmethod
    def _vector(text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [byte / 255.0 for byte in digest[:8]]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


def _build(output_dir: Path) -> None:
    documents = [
        Document(
            page_content="incident: suspicious login sequence",
            metadata={"source": "incident.csv", "row": 0},
        ),
        Document(
            page_content="incident: repeated failed authentication",
            metadata={"source": "incident.csv", "row": 1},
        ),
    ]
    ids = ["incident-0", "incident-1"]
    store = FAISS.from_documents(documents, DeterministicEmbeddings(), ids=ids)
    store.save_local(str(output_dir))


def _first_difference(left: bytes, right: bytes) -> int | None:
    for index, (left_byte, right_byte) in enumerate(zip(left, right)):
        if left_byte != right_byte:
            return index
    if len(left) != len(right):
        return min(len(left), len(right))
    return None


def test_two_consecutive_builds_report_independent_artifact_hashes(tmp_path: Path):
    """Capture independent SHA-256 values and locate any byte-level difference."""
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    _build(first_dir)
    _build(second_dir)

    first_faiss = (first_dir / "index.faiss").read_bytes()
    second_faiss = (second_dir / "index.faiss").read_bytes()
    first_pickle = (first_dir / "index.pkl").read_bytes()
    second_pickle = (second_dir / "index.pkl").read_bytes()

    first_faiss_sha = hashlib.sha256(first_faiss).hexdigest()
    second_faiss_sha = hashlib.sha256(second_faiss).hexdigest()
    first_pickle_sha = hashlib.sha256(first_pickle).hexdigest()
    second_pickle_sha = hashlib.sha256(second_pickle).hexdigest()

    print(f"index.faiss SHA-256 A: {first_faiss_sha}")
    print(f"index.faiss SHA-256 B: {second_faiss_sha}")
    print(f"index.pkl SHA-256 A: {first_pickle_sha}")
    print(f"index.pkl SHA-256 B: {second_pickle_sha}")
    print(f"index.faiss first differing byte: {_first_difference(first_faiss, second_faiss)}")
    print(f"index.pkl first differing byte: {_first_difference(first_pickle, second_pickle)}")

    assert first_faiss_sha == second_faiss_sha
    assert first_pickle_sha == second_pickle_sha


def test_pickle_payload_is_structurally_equal_across_builds(tmp_path: Path):
    """Inspect serialized docstore/mapping payload independently of pickle bytes."""
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    _build(first_dir)
    _build(second_dir)

    with (first_dir / "index.pkl").open("rb") as handle:
        first_docstore, first_mapping = pickle.load(handle)
    with (second_dir / "index.pkl").open("rb") as handle:
        second_docstore, second_mapping = pickle.load(handle)

    assert first_docstore._dict == second_docstore._dict
    assert first_mapping == second_mapping
    assert list(first_docstore._dict) == list(second_docstore._dict)
    assert first_mapping.keys() == second_mapping.keys()
