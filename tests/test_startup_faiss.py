"""Startup contract tests for verified FAISS initialization."""

from types import SimpleNamespace

import src.startup as startup


def test_startup_initializes_vector_store(monkeypatch):
    calls = []

    def fake_load():
        calls.append("load")

    fake_module = SimpleNamespace(
        vector_store_manager=SimpleNamespace(load=fake_load)
    )

    monkeypatch.setattr(startup, "check_runtime_dependencies", lambda: True)
    monkeypatch.setattr(
        startup.importlib,
        "import_module",
        lambda name: fake_module if name == "src.vector_store" else object(),
    )
    monkeypatch.setattr(startup, "_vector_store_initialized", False)

    assert startup.check_startup() is True
    assert calls == ["load"]
    assert startup._vector_store_initialized is True


def test_startup_fails_when_faiss_initialization_fails(monkeypatch):
    def fake_load():
        raise RuntimeError("FAISS index integrity check failed")

    fake_module = SimpleNamespace(
        vector_store_manager=SimpleNamespace(load=fake_load)
    )

    monkeypatch.setattr(startup, "check_runtime_dependencies", lambda: True)
    monkeypatch.setattr(
        startup.importlib,
        "import_module",
        lambda name: fake_module if name == "src.vector_store" else object(),
    )
    monkeypatch.setattr(startup, "_vector_store_initialized", False)

    assert startup.check_startup() is False
    assert startup._vector_store_initialized is False


def test_startup_fails_when_runtime_dependency_is_unavailable(monkeypatch):
    monkeypatch.setattr(startup, "check_runtime_dependencies", lambda: False)
    monkeypatch.setattr(startup, "_vector_store_initialized", False)

    assert startup.check_startup() is False
    assert startup._vector_store_initialized is False
