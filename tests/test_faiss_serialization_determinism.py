"""Diagnostics for FAISS artifact serialization reproducibility.

This test intentionally characterizes the current failure mode without changing
production integrity controls: the FAISS binary should be reproducible for the
same deterministic embeddings/documents, while LangChain's pickle metadata is
expected to differ when FAISS generates runtime UUID document IDs.
"""

from __future__ import annotations

import hashlib
import pickle
from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS


class DeterministicEmbeddings(Embeddings):
    """Small dependency-free deterministic embedding model for this diagnostic."""

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

    store = FAISS.from_documents(documents, DeterministicEmbeddings())
    store.save_local(str(output_dir))

    faiss_bytes = (output_dir / "index.faiss").read_bytes()
    pickle_bytes = (output_dir / "index.pkl").read_bytes()
    docstore, index_to_docstore_id = pickle.loads(pickle_bytes)

    return (
        hashlib.sha256(faiss_bytes).hexdigest(),
        hashlib.sha256(pickle_bytes).hexdigest(),
        tuple(index_to_docstore_id.values()),
    )


def test_same_inputs_isolate_pickle_metadata_nondeterminism(tmp_path: Path):
    """Prove whether nondeterminism is in FAISS bytes or pickle metadata."""
    first = _build_and_hash(tmp_path / "first")
    second = _build_and_hash(tmp_path / "second")

    first_faiss_sha, first_pickle_sha, first_ids = first
    second_faiss_sha, second_pickle_sha, second_ids = second

    assert first_faiss_sha == second_faiss_sha
    assert first_pickle_sha != second_pickle_sha
    assert first_ids != second_ids
    assert len(first_ids) == len(second_ids) == 2


def test_diagnostic_identifies_runtime_generated_document_ids(tmp_path: Path):
    """The current FAISS builder must not rely on runtime-generated IDs."""
    _, _, first_ids = _build_and_hash(tmp_path / "first")
    assert all(first_id for first_id in first_ids)
    assert all("incident-" not in first_id for first_id in first_ids)
