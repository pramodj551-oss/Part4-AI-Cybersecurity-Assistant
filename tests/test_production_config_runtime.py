"""Regression tests for production LLM runtime configuration validation."""

import importlib
import sys

import pytest


MODULE_NAME = "config.config"


def _load_config(monkeypatch, **env):
    """Load config.py with an isolated production environment."""
    defaults = {
        "APP_ENVIRONMENT": "production",
        "AUTH_USERNAME": "analyst",
        "AUTH_PASSWORD_HASH": "pbkdf2_sha256$600000$test$" + "a" * 64,
        "LLM_PROVIDER": "groq",
        "LLM_MODEL": "openai/gpt-oss-120b",
        "API_KEY": "test-api-key",
        "API_BASE_URL": "https://api.groq.com/openai/v1",
    }
    defaults.update(env)
    for key, value in defaults.items():
        monkeypatch.setenv(key, value)

    sys.modules.pop(MODULE_NAME, None)
    return importlib.import_module(MODULE_NAME)


def test_production_config_accepts_explicit_groq_runtime(monkeypatch):
    config = _load_config(monkeypatch)

    config.validate_production_config()
    assert config.APP_ENVIRONMENT == "production"
    assert config.LLM_PROVIDER == "groq"
    assert config.LLM_MODEL == "openai/gpt-oss-120b"
    assert config.API_BASE_URL == "https://api.groq.com/openai/v1"


def test_production_config_rejects_localhost_runtime(monkeypatch):
    config = _load_config(monkeypatch, API_BASE_URL="http://localhost:11434/v1")
    with pytest.raises(RuntimeError, match="API_BASE_URL"):
        config.validate_production_config()


def test_production_config_rejects_default_llm_model(monkeypatch):
    config = _load_config(monkeypatch, LLM_MODEL="llama2")
    with pytest.raises(RuntimeError, match="LLM_MODEL"):
        config.validate_production_config()


def test_production_config_rejects_default_api_key(monkeypatch):
    config = _load_config(monkeypatch, API_KEY="ollama")
    with pytest.raises(RuntimeError, match="API_KEY"):
        config.validate_production_config()
