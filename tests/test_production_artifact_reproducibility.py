"""Cross-build reproducibility audit for the real production incident dataset."""

from __future__ import annotations

import hashlib
import os
import pickle
import pickletools
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET = REPO_ROOT / "data" / "cybersecurity_incident_reports.csv"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_build(output_dir: Path, hash_seed: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = hash_seed
    env["APP_ENVIRONMENT"] = "development"
    env["HF_HOME"] = str(output_dir / "hf-cache")
    env["PYTHONPATH"] = str(REPO_ROOT)
    subprocess.run(
        [
            sys.executable,
            "scripts/build_vectorstore.py",
            "--output",
            str(output_dir / "faiss_index"),
        ],
        cwd=REPO_ROOT,
        env=env,
        check=True,
        text=True,
    )


def _first_difference(left: bytes, right: bytes) -> int | None:
    for index, (left_byte, right_byte) in enumerate(zip(left, right)):
        if left_byte != right_byte:
            return index
    if len(left) != len(right):
        return min(len(left), len(right))
    return None


def _opcode_window(data: bytes, center: int, radius: int = 96) -> list[str]:
    start = max(0, center - radius)
    end = min(len(data), center + radius)
    return [
        f"{position}: {opcode.name} {arg!r}"
        for opcode, arg, position in pickletools.genops(data)
        if start <= position < end
    ]


def _artifact_structure(path: Path) -> tuple[list[str], dict[int, str], list[tuple[str, str, str]]]:
    with (path / "index.pkl").open("rb") as handle:
        docstore, mapping = pickle.load(handle)

    ordered_ids = list(docstore._dict)
    documents = []
    for doc_id in ordered_ids:
        document = docstore._dict[doc_id]
        documents.append(
            (
                str(doc_id),
                str(document.page_content),
                repr(document.metadata),
            )
        )
    return ordered_ids, mapping, documents


def _report(
    first_pickle: bytes,
    second_pickle: bytes,
    diff: int | None,
    first_dir: Path,
    second_dir: Path,
) -> str:
    if diff is None:
        return "index.pkl byte streams are identical"

    start = max(0, diff - 96)
    end = min(max(len(first_pickle), len(second_pickle)), diff + 96)
    return "\n".join(
        [
            f"index.pkl first differing byte: {diff}",
            f"index.pkl lengths: A={len(first_pickle)} B={len(second_pickle)}",
            "index.pkl opcode window A:",
            *_opcode_window(first_pickle, diff),
            "index.pkl opcode window B:",
            *_opcode_window(second_pickle, diff),
            f"index.pkl bytes A[{diff}:{diff + 64}]: "
            f"{first_pickle[diff:diff + 64].hex()}",
            f"index.pkl bytes B[{diff}:{diff + 64}]: "
            f"{second_pickle[diff:diff + 64].hex()}",
            f"index.pkl context A[{start}:{end}]: {first_pickle[start:end].hex()}",
            f"index.pkl context B[{start}:{end}]: {second_pickle[start:end].hex()}",
            f"index.faiss A: {_sha256(first_dir / 'faiss_index' / 'index.faiss')}",
            f"index.faiss B: {_sha256(second_dir / 'faiss_index' / 'index.faiss')}",
        ]
    )


def test_production_dataset_fingerprint_is_stable():
    assert DATASET.exists()
    dataset_sha = _sha256(DATASET)
    print(f"production dataset: {DATASET}")
    print(f"production dataset SHA-256: {dataset_sha}")
    print(f"production dataset bytes: {DATASET.stat().st_size}")


def test_real_production_vectorstore_is_byte_reproducible(tmp_path: Path):
    first_dir = tmp_path / "build-a"
    second_dir = tmp_path / "build-b"

    _run_build(first_dir, "1")
    _run_build(second_dir, "2")

    first_store = first_dir / "faiss_index"
    second_store = second_dir / "faiss_index"

    first_faiss = (first_store / "index.faiss").read_bytes()
    second_faiss = (second_store / "index.faiss").read_bytes()
    first_pickle = (first_store / "index.pkl").read_bytes()
    second_pickle = (second_store / "index.pkl").read_bytes()

    first_faiss_sha = _sha256(first_store / "index.faiss")
    second_faiss_sha = _sha256(second_store / "index.faiss")
    first_pickle_sha = _sha256(first_store / "index.pkl")
    second_pickle_sha = _sha256(second_store / "index.pkl")

    faiss_diff = _first_difference(first_faiss, second_faiss)
    pickle_diff = _first_difference(first_pickle, second_pickle)

    print(f"index.faiss SHA-256 A: {first_faiss_sha}")
    print(f"index.faiss SHA-256 B: {second_faiss_sha}")
    print(f"index.pkl SHA-256 A: {first_pickle_sha}")
    print(f"index.pkl SHA-256 B: {second_pickle_sha}")
    print(f"index.faiss first differing byte: {faiss_diff}")
    print(f"index.pkl first differing byte: {pickle_diff}")

    first_ids, first_mapping, first_documents = _artifact_structure(first_store)
    second_ids, second_mapping, second_documents = _artifact_structure(second_store)

    print(f"docstore IDs equal: {first_ids == second_ids}")
    print(f"index mapping equal: {first_mapping == second_mapping}")
    print(f"documents equal: {first_documents == second_documents}")

    if pickle_diff is not None:
        report = _report(first_pickle, second_pickle, pickle_diff, first_dir, second_dir)
        print(report)
        assert first_pickle_sha == second_pickle_sha, report

    assert first_faiss_sha == second_faiss_sha
    assert first_ids == second_ids
    assert first_mapping == second_mapping
    assert first_documents == second_documents
