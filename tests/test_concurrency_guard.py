"""Contract tests for bounded RAG concurrency control."""

from __future__ import annotations

import threading

import pytest

from src.concurrency import (
    DEFAULT_MAX_IN_FLIGHT,
    MAX_ALLOWED_IN_FLIGHT,
    ConcurrencyLimitError,
    RAGConcurrencyGuard,
    get_max_in_flight,
)
from src.rag_pipeline import RAGPipeline


def test_invalid_or_unsafe_config_fails_closed(monkeypatch):
    for value in ("invalid", "0", "-1"):
        monkeypatch.setenv("RAG_MAX_IN_FLIGHT", value)
        assert get_max_in_flight() == DEFAULT_MAX_IN_FLIGHT


def test_config_is_bounded(monkeypatch):
    monkeypatch.setenv("RAG_MAX_IN_FLIGHT", str(MAX_ALLOWED_IN_FLIGHT + 10))
    assert get_max_in_flight() == MAX_ALLOWED_IN_FLIGHT


def test_guard_rejects_when_capacity_is_full():
    guard = RAGConcurrencyGuard(max_in_flight=1)
    guard.acquire()
    try:
        with pytest.raises(ConcurrencyLimitError):
            guard.acquire()
    finally:
        guard.release()


def test_guard_releases_after_success_and_exception():
    guard = RAGConcurrencyGuard(max_in_flight=1)

    with guard:
        pass
    with guard:
        pass

    with pytest.raises(RuntimeError):
        with guard:
            raise RuntimeError("simulated failure")

    with guard:
        pass


def test_rag_pipeline_controls_expensive_path(monkeypatch):
    guard = RAGConcurrencyGuard(max_in_flight=1)
    pipeline = RAGPipeline(concurrency_guard=guard)
    started = threading.Event()
    unblock = threading.Event()

    def blocking_retrieve(question):
        started.set()
        unblock.wait(2)
        return []

    monkeypatch.setattr(
        "src.rag_pipeline.retriever_manager.retrieve",
        blocking_retrieve,
    )
    monkeypatch.setattr(
        "src.rag_pipeline.prompt_builder.build_prompt",
        lambda question, documents: question,
    )
    monkeypatch.setattr(
        "src.rag_pipeline.prompt_builder.system_prompt",
        "test-system",
        raising=False,
    )
    monkeypatch.setattr(
        "src.rag_pipeline.llm_manager.generate",
        lambda prompt, system_prompt: {"answer": "ok"},
    )
    monkeypatch.setattr(
        "src.rag_pipeline.prompt_builder.extract_sources",
        lambda documents: [],
    )

    result_holder = {}

    def run_first_request():
        result_holder["result"] = pipeline.answer("first")

    worker = threading.Thread(target=run_first_request)
    worker.start()
    assert started.wait(1)

    with pytest.raises(ConcurrencyLimitError):
        pipeline.answer("second")

    unblock.set()
    worker.join(timeout=2)
    assert not worker.is_alive()
    assert result_holder["result"]["answer"] == "ok"


def test_empty_question_does_not_consume_guard():
    guard = RAGConcurrencyGuard(max_in_flight=1)
    pipeline = RAGPipeline(concurrency_guard=guard)

    with pytest.raises(ValueError):
        pipeline.answer("   ")

    with guard:
        pass
