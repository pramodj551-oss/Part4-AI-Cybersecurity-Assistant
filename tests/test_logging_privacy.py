import logging

from src.utils import PrivacyRedactionFilter, audit_event, redact_sensitive_data


def test_redacts_common_credential_values():
    message = (
        "api_key=super-secret password=hunter2 "
        "Authorization: Bearer abc123 secret=hidden token=tok-value"
    )

    safe = redact_sensitive_data(message)

    assert "super-secret" not in safe
    assert "hunter2" not in safe
    assert "abc123" not in safe
    assert "hidden" not in safe
    assert "tok-value" not in safe
    assert safe.count("[REDACTED]") == 5


def test_logging_filter_redacts_record_before_handler_output():
    record = logging.LogRecord(
        name="security",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="API_KEY=%s password=%s",
        args=("secret-key", "secret-password"),
        exc_info=None,
    )

    assert PrivacyRedactionFilter().filter(record) is True
    assert record.args == ()
    assert "secret-key" not in record.getMessage()
    assert "secret-password" not in record.getMessage()
    assert record.getMessage().count("[REDACTED]") == 2


def test_audit_event_is_privacy_safe(caplog):
    logger = logging.getLogger("privacy-audit-test")

    with caplog.at_level(logging.INFO, logger=logger.name):
        audit_event(
            logger,
            "authentication_failure",
            username="analyst",
            api_key="do-not-log-this",
            source="login",
        )

    message = caplog.records[-1].getMessage()
    assert "audit_event=authentication_failure" in message
    assert "do-not-log-this" not in message
    assert "[REDACTED]" in message
    assert "username=analyst" in message


def test_redaction_preserves_non_sensitive_operational_context():
    message = "event=rag_retrieval documents=3 latency_ms=42"

    safe = redact_sensitive_data(message)

    assert safe == message
