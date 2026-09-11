"""Startup contract tests for verified FAISS initialization."""

import sys
from types import SimpleNamespace

import src.startup as startup


def _fake_vector_store(load):
    return SimpleNamespace(vector_store_manager=SimpleNamespace(load=load))


def test_startup_initializes_vector_store(monkeypatch):
    calls = []

    def fake_load():
        calls.append("load")

    monkeypatch.setitem(sys.modules, "src.vector_store", _fake_vector_store(fake_load))
    monkeypatch.setattr(startup, "check_runtime_dependencies", lambda: True)
    monkeypatch.setattr(startup, "_vector_store_initialized", False)
    monkeypatch.setenv("APP_ENVIRONMENT", "production")

    assert startup.check_startup() is True
    assert calls == ["load"]
    assert startup._vector_store_initialized is True


def test_startup_fails_when_faiss_initialization_fails(monkeypatch):
    def fake_load():
        raise RuntimeError("FAISS index integrity check failed")

    monkeypatch.setitem(sys.modules, "src.vector_store", _fake_vector_store(fake_load))
    monkeypatch.setattr(startup, "check_runtime_dependencies", lambda: True)
    monkeypatch.setattr(startup, "_vector_store_initialized", False)
    monkeypatch.setenv("APP_ENVIRONMENT", "production")

    assert startup.check_startup() is False
    assert startup._vector_store_initialized is False


def test_startup_fails_when_runtime_dependency_is_unavailable(monkeypatch):
    monkeypatch.setattr(startup, "check_runtime_dependencies", lambda: False)
    monkeypatch.setattr(startup, "_vector_store_initialized", False)

    assert startup.check_startup() is False
    assert startup._vector_store_initialized is False
