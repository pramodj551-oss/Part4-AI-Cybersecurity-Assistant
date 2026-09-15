from http import HTTPStatus
from unittest.mock import patch

from src import api_health


def test_health_contract_is_lightweight_and_ok():
    status, body = api_health.health_response()

    assert status == HTTPStatus.OK
    assert body == {"status": "ok"}


def test_readiness_contract_is_ready_when_startup_succeeds():
    with patch("src.api_health.check_startup", return_value=True):
        status, body = api_health.readiness_response()

    assert status == HTTPStatus.OK
    assert body == {"status": "ready"}


def test_readiness_contract_is_unavailable_when_startup_fails():
    with patch("src.api_health.check_startup", return_value=False):
        status, body = api_health.readiness_response()

    assert status == HTTPStatus.SERVICE_UNAVAILABLE
    assert body == {"status": "not_ready"}


def test_contract_paths_are_stable():
    assert api_health.HEALTH_PATH == "/health"
    assert api_health.READY_PATH == "/ready"
