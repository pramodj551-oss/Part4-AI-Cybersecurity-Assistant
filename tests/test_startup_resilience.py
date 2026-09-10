"""Regression coverage for startup dependency failure and recovery."""

from __future__ import annotations

import importlib

import scripts.healthcheck as healthcheck
from src import startup


def test_missing_runtime_dependency_fails_closed(monkeypatch):
    real_import = importlib.import_module

    def fail_required(module_name, package=None):
        if module_name == "src.retriever":
            raise ModuleNotFoundError("simulated missing dependency")
        return real_import(module_name, package)

    monkeypatch.setattr(startup.importlib, "import_module", fail_required)

    assert startup.check_runtime_dependencies() is False
    assert startup.check_startup() is False


def test_startup_recovers_when_dependency_becomes_available(monkeypatch):
    state = {"available": False}

    def recoverable_import(module_name, package=None):
        if module_name == "src.retriever" and not state["available"]:
            raise ImportError("simulated unavailable dependency")
        return object()

    monkeypatch.setattr(startup.importlib, "import_module", recoverable_import)

    assert startup.check_startup() is False

    state["available"] = True

    assert startup.check_startup() is True


def test_readiness_fails_closed_when_startup_dependency_is_unavailable(monkeypatch):
    monkeypatch.setattr(healthcheck, "check_health", lambda port=8502: True)
    monkeypatch.setattr(healthcheck, "check_startup", lambda: False, raising=False)

    assert healthcheck.check_readiness() is False


def test_readiness_recovers_after_startup_dependency_returns(monkeypatch):
    state = {"ready": False}
    monkeypatch.setattr(healthcheck, "check_health", lambda port=8502: True)
    monkeypatch.setattr(healthcheck, "check_startup", lambda: state["ready"], raising=False)

    assert healthcheck.check_readiness() is False

    state["ready"] = True

    assert healthcheck.check_readiness() is True


def test_healthcheck_process_failure_remains_not_ready(monkeypatch):
    monkeypatch.setattr(healthcheck, "check_health", lambda port=8502: False)
    monkeypatch.setattr(healthcheck, "check_startup", lambda: True, raising=False)

    assert healthcheck.check_readiness() is False
