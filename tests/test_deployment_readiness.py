from pathlib import Path
from unittest.mock import patch

from scripts import healthcheck


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_health_check_uses_streamlit_native_endpoint():
    with patch("scripts.healthcheck.urlopen", return_value=_Response()) as mock_urlopen:
        assert healthcheck.check_health(8502) is True
    mock_urlopen.assert_called_once_with(
        "http://127.0.0.1:8502/_stcore/health", timeout=3
    )


def test_health_check_fails_when_streamlit_is_unavailable():
    with patch(
        "scripts.healthcheck.urlopen", side_effect=healthcheck.URLError("down")
    ):
        assert healthcheck.check_health(8502) is False


def test_readiness_fails_when_streamlit_is_unavailable():
    with patch(
        "scripts.healthcheck.urlopen", side_effect=healthcheck.URLError("down")
    ):
        assert healthcheck.check_readiness(8502) is False


def test_production_readiness_validates_configuration():
    with patch("scripts.healthcheck.urlopen", return_value=_Response()), patch.dict(
        "os.environ", {"APP_ENVIRONMENT": "production"}, clear=False
    ), patch(
        "builtins.__import__",
        side_effect=_production_config_import,
    ):
        assert healthcheck.check_readiness(8502) is True
    assert _production_config_import.validate_called is True


def test_non_production_readiness_does_not_require_production_config():
    with patch("scripts.healthcheck.urlopen", return_value=_Response()), patch.dict(
        "os.environ", {"APP_ENVIRONMENT": "development"}, clear=False
    ):
        assert healthcheck.check_readiness(8502) is True


def test_dockerfile_declares_secure_runtime_contract():
    dockerfile = Path("Dockerfile").read_text()
    assert "FROM python:3.11-slim" in dockerfile
    assert "USER app" in dockerfile
    assert "EXPOSE 8502" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "scripts/healthcheck.py --health --port 8502" in dockerfile
    assert "pip install --no-cache-dir --require-hashes -r requirements.txt" in dockerfile


def _production_config_import(name, *args, **kwargs):
    if name == "config.config":
        class _ConfigModule:
            @staticmethod
            def validate_production_config():
                _production_config_import.validate_called = True

        return _ConfigModule
    import builtins

    return builtins.__import__(name, *args, **kwargs)


_production_config_import.validate_called = False
