"""Regression tests for production configuration fail-closed behavior."""

import importlib

import pytest


@pytest.fixture
def config_module(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "development")
    import config.config as config

    return importlib.reload(config)


def test_development_keeps_local_defaults(config_module):
    assert config_module.APP_ENVIRONMENT == "development"
    assert config_module.API_KEY == "ollama"
    assert config_module.API_BASE_URL == "http://localhost:11434/v1"


def test_production_rejects_missing_required_configuration(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "production")
    for name in (
        "AUTH_USERNAME",
        "AUTH_PASSWORD_HASH",
        "API_KEY",
        "LLM_PROVIDER",
        "LLM_MODEL",
        "API_BASE_URL",
    ):
        monkeypatch.delenv(name, raising=False)

    import config.config as config

    with pytest.raises(RuntimeError, match="Production configuration is incomplete"):
        importlib.reload(config)


def test_production_rejects_insecure_defaults(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_USERNAME", "analyst")
    monkeypatch.setenv(
        "AUTH_PASSWORD_HASH",
        "pbkdf2_sha256$600000$production-salt$0123456789abcdef",
    )
    monkeypatch.setenv("API_KEY", "ollama")
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_MODEL", "llama2")
    monkeypatch.setenv("API_BASE_URL", "http://localhost:11434/v1")

    import config.config as config

    with pytest.raises(RuntimeError, match="insecure/default values"):
        importlib.reload(config)


def test_production_accepts_explicit_non_default_configuration(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_USERNAME", "prod-analyst")
    monkeypatch.setenv(
        "AUTH_PASSWORD_HASH",
        "pbkdf2_sha256$600000$production-salt$0123456789abcdef",
    )
    monkeypatch.setenv("API_KEY", "production-secret-reference")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "production-model")
    monkeypatch.setenv("API_BASE_URL", "https://llm.internal.example/v1")

    import config.config as config

    config = importlib.reload(config)
    assert config.APP_ENVIRONMENT == "production"
    assert config.LLM_MODEL == "production-model"
    assert config.API_BASE_URL == "https://llm.internal.example/v1"
