"""Root-cause diagnostics for FAISS artifact serialization determinism."""

from __future__ import annotations

import hashlib
import os
import pickle
import pickletools
import subprocess
import sys
from pathlib import Path


def _build_in_subprocess(output_dir: Path, hash_seed: str) -> tuple[str, str]:
    """Build an artifact in an isolated Python process with a fixed hash seed."""
    output_dir.mkdir(parents=True, exist_ok=True)
    script = r'''
import hashlib
import sys
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from src.vector_store import VectorStoreManager

class DeterministicEmbeddings(Embeddings):
    @staticmethod
    def _vector(text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [byte / 255.0 for byte in digest[:8]]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)

output_dir = Path(sys.argv[1])
documents = [
    Document(
        id="incident-0",
        page_content="incident: suspicious login sequence",
        metadata={"source": "incident.csv", "row": 0},
    ),
    Document(
        id="incident-1",
        page_content="incident: repeated failed authentication",
        metadata={"source": "incident.csv", "row": 1},
    ),
]
ids = ["incident-0", "incident-1"]
store = FAISS.from_documents(documents, DeterministicEmbeddings(), ids=ids)
store.save_local(str(output_dir))
VectorStoreManager._write_deterministic_metadata(output_dir)
'''
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = hash_seed
    subprocess.run(
        [sys.executable, "-c", script, str(output_dir)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    faiss_sha = hashlib.sha256((output_dir / "index.faiss").read_bytes()).hexdigest()
    pickle_sha = hashlib.sha256((output_dir / "index.pkl").read_bytes()).hexdigest()
    return faiss_sha, pickle_sha


def _first_difference(left: bytes, right: bytes) -> int | None:
    for index, (left_byte, right_byte) in enumerate(zip(left, right)):
        if left_byte != right_byte:
            return index
    if len(left) != len(right):
        return min(len(left), len(right))
    return None


def _pickle_payload(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def _opcode_window(data: bytes, center: int, radius: int = 90) -> list[str]:
    """Return pickle opcode text around a byte offset for root-cause evidence."""
    start = max(0, center - radius)
    end = min(len(data), center + radius)
    lines: list[str] = []
    for opcode, arg, position in pickletools.genops(data):
        if start <= position < end:
            lines.append(f"{position}: {opcode.name} {arg!r}")
    return lines


def test_cross_process_faiss_artifacts_are_byte_identical(tmp_path: Path):
    """Two isolated builds must reproduce identical FAISS and pickle bytes."""
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_faiss_sha, first_pickle_sha = _build_in_subprocess(first_dir, "1")
    second_faiss_sha, second_pickle_sha = _build_in_subprocess(second_dir, "2")

    first_faiss = (first_dir / "index.faiss").read_bytes()
    second_faiss = (second_dir / "index.faiss").read_bytes()
    first_pickle = (first_dir / "index.pkl").read_bytes()
    second_pickle = (second_dir / "index.pkl").read_bytes()

    faiss_diff = _first_difference(first_faiss, second_faiss)
    pickle_diff = _first_difference(first_pickle, second_pickle)
    print(f"index.faiss SHA-256 A: {first_faiss_sha}")
    print(f"index.faiss SHA-256 B: {second_faiss_sha}")
    print(f"index.pkl SHA-256 A: {first_pickle_sha}")
    print(f"index.pkl SHA-256 B: {second_pickle_sha}")
    print(f"index.faiss first differing byte: {faiss_diff}")
    print(f"index.pkl first differing byte: {pickle_diff}")
    if pickle_diff is not None:
        print("index.pkl opcode window A:")
        print("\n".join(_opcode_window(first_pickle, pickle_diff)))
        print("index.pkl opcode window B:")
        print("\n".join(_opcode_window(second_pickle, pickle_diff)))
        print(f"index.pkl bytes A[{pickle_diff}:{pickle_diff + 32}]: {first_pickle[pickle_diff:pickle_diff + 32].hex()}")
        print(f"index.pkl bytes B[{pickle_diff}:{pickle_diff + 32}]: {second_pickle[pickle_diff:pickle_diff + 32].hex()}")

    assert first_faiss_sha == second_faiss_sha
    assert first_pickle_sha == second_pickle_sha


def test_cross_process_pickle_payload_is_structurally_equal(tmp_path: Path):
    """If bytes differ, distinguish payload drift from pickle-byte drift."""
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    _build_in_subprocess(first_dir, "1")
    _build_in_subprocess(second_dir, "2")

    first_docstore, first_mapping = _pickle_payload(first_dir / "index.pkl")
    second_docstore, second_mapping = _pickle_payload(second_dir / "index.pkl")

    first_ids = list(first_docstore._dict)
    second_ids = list(second_docstore._dict)
    first_documents = [first_docstore._dict[key] for key in first_ids]
    second_documents = [second_docstore._dict[key] for key in second_ids]

    assert first_ids == second_ids
    assert first_mapping == second_mapping
    assert first_documents == second_documents
