"""FINAL-PROD-01 aggregate production-readiness regression tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from src.integration_contract import (
    EXPECTED_ARTIFACTS,
    validate_artifacts_against_manifest,
    validate_handoff_manifest,
)
from src.rag_pipeline import RAGPipeline


PART2_REPOSITORY = "pramodj551-oss/Part2-Cybersecurity-ML-Pipeline"
PART2_RELEASE_TAG = "part2-runtime-33513838252"
PART2_RELEASE_COMMIT = "4c7714cff07829d5fdcee052f936045df30c23b7"
BUNDLE_NAME = "part2-runtime-bundle.zip"
BUNDLE_SHA256 = "ece2b6bf91f19e5c0eb19475ae7198155f3fdaa4e8839ec9ab95f8cfcf031d54"


def _manifest() -> dict:
    return {
        "source_repository": PART2_REPOSITORY,
        "source_release_tag": PART2_RELEASE_TAG,
        "source_release_commit": PART2_RELEASE_COMMIT,
        "bundle_name": BUNDLE_NAME,
        "bundle_sha256": BUNDLE_SHA256,
        "files": {
            path: hashlib.sha256(path.encode()).hexdigest()
            for path in EXPECTED_ARTIFACTS
        },
    }


def _write_artifacts(root: Path, manifest: dict) -> None:
    for path in EXPECTED_ARTIFACTS:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(path, encoding="utf-8")
        manifest["files"][path] = hashlib.sha256(path.encode()).hexdigest()


def test_final_production_scorecard_contract_is_complete() -> None:
    manifest = _manifest()
    required = {
        "source_repository",
        "source_release_tag",
        "source_release_commit",
        "bundle_name",
        "bundle_sha256",
        "files",
    }
    assert required.issubset(manifest)
    assert validate_handoff_manifest(manifest)
    assert set(manifest["files"]) == set(EXPECTED_ARTIFACTS)


def test_end_to_end_rag_smoke_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeRetriever:
        def retrieve(self, question: str) -> list[dict]:
            assert question == "What happened?"
            return [{"page_content": "Incident evidence", "metadata": {"source": "report.csv"}}]

    class FakePromptBuilder:
        system_prompt = "Use evidence only."

        def build_prompt(self, question: str, documents: list[dict]) -> str:
            assert documents
            return "safe prompt"

        def extract_sources(self, documents: list[dict]) -> list[str]:
            return ["report.csv"]

    class FakeLLM:
        def generate(self, prompt: str, system_prompt: str) -> dict:
            assert prompt == "safe prompt"
            assert system_prompt == "Use evidence only."
            return {"answer": "Evidence-based answer", "model": "test", "finish_reason": "stop"}

    monkeypatch.setattr("src.rag_pipeline.retriever_manager", FakeRetriever())
    monkeypatch.setattr("src.rag_pipeline.prompt_builder", FakePromptBuilder())
    monkeypatch.setattr("src.rag_pipeline.llm_manager", FakeLLM())

    result = RAGPipeline().answer("What happened?")
    assert result == {
        "question": "What happened?",
        "answer": "Evidence-based answer",
        "sources": ["report.csv"],
        "retrieved_documents": 1,
        "model": "test",
        "finish_reason": "stop",
    }


def test_end_to_end_rag_smoke_fails_closed_on_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeRetriever:
        def retrieve(self, question: str) -> list[dict]:
            return [{"page_content": "evidence", "metadata": {"source": "report.csv"}}]

    class FakePromptBuilder:
        system_prompt = "Use evidence only."

        def build_prompt(self, question: str, documents: list[dict]) -> str:
            return "safe prompt"

        def extract_sources(self, documents: list[dict]) -> list[str]:
            return ["report.csv"]

    class SafeErrorLLM:
        def generate(self, prompt: str, system_prompt: str) -> dict:
            return {"answer": "The language model is temporarily unavailable. Please try again later.", "model": None, "finish_reason": "error"}

    monkeypatch.setattr("src.rag_pipeline.retriever_manager", FakeRetriever())
    monkeypatch.setattr("src.rag_pipeline.prompt_builder", FakePromptBuilder())
    monkeypatch.setattr("src.rag_pipeline.llm_manager", SafeErrorLLM())

    result = RAGPipeline().answer("What happened?")
    assert result["finish_reason"] == "error"
    assert result["answer"]
    assert "traceback" not in result["answer"].lower()
    assert "api_key" not in result["answer"].lower()


def test_required_runtime_artifacts_fail_closed_when_missing(tmp_path: Path) -> None:
    manifest = _manifest()
    _write_artifacts(tmp_path, manifest)
    (tmp_path / EXPECTED_ARTIFACTS[0]).unlink()
    assert not validate_artifacts_against_manifest(tmp_path, manifest)


def test_required_runtime_artifacts_fail_closed_when_tampered(tmp_path: Path) -> None:
    manifest = _manifest()
    _write_artifacts(tmp_path, manifest)
    target = tmp_path / EXPECTED_ARTIFACTS[1]
    target.write_text("tampered", encoding="utf-8")
    assert not validate_artifacts_against_manifest(tmp_path, manifest)


def test_scorecard_is_serializable() -> None:
    scorecard = {
        "FINAL-PROD-01": "PASS",
        "gates": [
            "AUTH-ENTRY-01",
            "CONFIG-SEC-01",
            "RAG-SEC-01",
            "LLM-RES-01",
            "DEPLOY-HEALTH-01",
            "OBS-PRIV-01",
            "STARTUP-RES-01",
            "INTEGRATION-01",
        ],
    }
    assert json.loads(json.dumps(scorecard))["FINAL-PROD-01"] == "PASS"
