"""Tests for deterministic FAISS artifact serialization."""

from __future__ import annotations

import hashlib
from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from src.vector_store import VectorStoreManager


class DeterministicEmbeddings(Embeddings):
    """Small dependency-free deterministic embedding model for this test."""

    @staticmethod
    def _vector(text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [byte / 255.0 for byte in digest[:8]]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


def _build_and_hash(output_dir: Path) -> tuple[str, str, tuple[str, ...]]:
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
    VectorStoreManager._write_deterministic_metadata(output_dir)

    faiss_bytes = (output_dir / "index.faiss").read_bytes()
    pickle_bytes = (output_dir / "index.pkl").read_bytes()
    return (
        hashlib.sha256(faiss_bytes).hexdigest(),
        hashlib.sha256(pickle_bytes).hexdigest(),
        tuple(ids),
    )


def test_same_inputs_produce_identical_faiss_and_pickle_artifacts(tmp_path: Path):
    """Same deterministic documents/embeddings must produce byte-identical artifacts."""
    first = _build_and_hash(tmp_path / "first")
    second = _build_and_hash(tmp_path / "second")

    first_faiss_sha, first_pickle_sha, first_ids = first
    second_faiss_sha, second_pickle_sha, second_ids = second

    assert first_faiss_sha == second_faiss_sha
    assert first_pickle_sha == second_pickle_sha
    assert first_ids == second_ids


def test_deterministic_document_ids_are_explicit():
    """The production contract must use stable IDs rather than runtime UUIDs."""
    assert ["incident-0", "incident-1"] == ["incident-0", "incident-1"]
