from types import SimpleNamespace

import pytest

from src import llm as llm_module


class APIConnectionError(Exception):
    pass


class APITimeoutError(Exception):
    pass


def make_response(answer="Recovered response", finish_reason="stop"):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=answer),
                finish_reason=finish_reason,
            )
        ]
    )


def test_client_uses_bounded_timeout_and_explicit_retry_control(monkeypatch):
    captured = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(llm_module, "OpenAI", FakeOpenAI)
    manager = llm_module.LLMManager()

    assert manager.client is not None
    assert captured["timeout"] == llm_module.LLM_TIMEOUT_SECONDS
    assert captured["timeout"] > 0
    assert captured["max_retries"] == 0


def test_transient_provider_failure_recovers(monkeypatch):
    calls = {"count": 0}
    sleeps = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls["count"] += 1
            if calls["count"] == 1:
                raise APIConnectionError("provider unavailable")
            return make_response()

    class FakeClient:
        chat = SimpleNamespace(completions=FakeCompletions())

    manager = llm_module.LLMManager.__new__(llm_module.LLMManager)
    manager.client = FakeClient()
    monkeypatch.setattr(llm_module.time, "sleep", sleeps.append)

    result = manager.generate("test prompt")

    assert calls["count"] == 2
    assert sleeps == [llm_module.LLM_BACKOFF_SECONDS]
    assert result["answer"] == "Recovered response"
    assert result["finish_reason"] == "stop"


def test_timeout_failure_retries_with_bounded_attempts(monkeypatch):
    calls = {"count": 0}
    sleeps = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls["count"] += 1
            raise APITimeoutError("LLM timed out")

    class FakeClient:
        chat = SimpleNamespace(completions=FakeCompletions())

    manager = llm_module.LLMManager.__new__(llm_module.LLMManager)
    manager.client = FakeClient()
    monkeypatch.setattr(llm_module.time, "sleep", sleeps.append)

    result = manager.generate("test prompt")

    assert calls["count"] == llm_module.LLM_MAX_ATTEMPTS
    assert sleeps == [0.5, 1.0]
    assert result["finish_reason"] == "error"
    assert result["answer"] == llm_module.SAFE_ERROR_MESSAGE


def test_non_retryable_failure_fails_closed_without_retry(monkeypatch):
    calls = {"count": 0}
    sleeps = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls["count"] += 1
            raise RuntimeError("unexpected provider failure")

    class FakeClient:
        chat = SimpleNamespace(completions=FakeCompletions())

    manager = llm_module.LLMManager.__new__(llm_module.LLMManager)
    manager.client = FakeClient()
    monkeypatch.setattr(llm_module.time, "sleep", sleeps.append)

    result = manager.generate("test prompt")

    assert calls["count"] == 1
    assert sleeps == []
    assert result["finish_reason"] == "error"
    assert "unexpected provider failure" not in result["answer"]
    assert "test prompt" not in result["answer"]


def test_empty_prompt_still_rejected():
    manager = llm_module.LLMManager.__new__(llm_module.LLMManager)
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        manager.generate("   ")
