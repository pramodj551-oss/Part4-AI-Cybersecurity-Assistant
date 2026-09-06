import pytest

import src.auth as auth


def test_password_hash_round_trip():
    encoded = auth.hash_password("Correct-Horse-Battery-Staple", salt="00112233445566778899aabbccddeeff", iterations=100_000)
    assert auth.verify_password("Correct-Horse-Battery-Staple", encoded)
    assert not auth.verify_password("wrong-password", encoded)


def test_authenticate_accepts_valid_user_and_rejects_invalid(monkeypatch):
    encoded = auth.hash_password("strong-test-password", salt="00112233445566778899aabbccddeeff", iterations=100_000)
    monkeypatch.setenv("AUTH_USERNAME", "analyst")
    monkeypatch.setenv("AUTH_PASSWORD_HASH", encoded)

    assert auth.authenticate("analyst", "strong-test-password")
    assert not auth.authenticate("attacker", "strong-test-password")
    assert not auth.authenticate("analyst", "wrong-password")


def test_missing_auth_configuration_fails_closed(monkeypatch):
    monkeypatch.delenv("AUTH_USERNAME", raising=False)
    monkeypatch.delenv("AUTH_PASSWORD_HASH", raising=False)

    with pytest.raises(RuntimeError, match="Authentication is not configured"):
        auth.authenticate("analyst", "anything")


def test_expired_session_is_not_authenticated(monkeypatch):
    session = {
        "authenticated": True,
        "auth_user": "analyst",
        "auth_role": "analyst",
        "auth_expires_at": 100.0,
    }
    monkeypatch.setattr(auth.st, "session_state", session)
    monkeypatch.setattr(auth.time, "time", lambda: 101.0)

    assert not auth.is_authenticated()
    assert session == {}


def test_logout_invalidates_session(monkeypatch):
    session = {
        "authenticated": True,
        "auth_user": "analyst",
        "auth_role": "analyst",
        "auth_expires_at": 9999999999.0,
    }
    monkeypatch.setattr(auth.st, "session_state", session)

    auth.logout()

    assert session == {}
    assert not auth.is_authenticated()


def test_role_authorization_is_based_on_authenticated_session(monkeypatch):
    session = {
        "authenticated": True,
        "auth_user": "analyst",
        "auth_role": "analyst",
        "auth_expires_at": 9999999999.0,
    }
    monkeypatch.setattr(auth.st, "session_state", session)
    monkeypatch.setattr(auth.time, "time", lambda: 100.0)

    assert auth.current_role() == "analyst"
    assert "admin" != auth.current_role()
