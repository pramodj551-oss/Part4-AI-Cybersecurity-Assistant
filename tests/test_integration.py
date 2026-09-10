import hashlib
import json

import pytest

from src.integration_contract import (
    EXPECTED_ARTIFACTS,
    IntegrationContractError,
    load_handoff_manifest,
    validate_artifacts_against_manifest,
    validate_handoff_manifest,
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest() -> dict:
    return {
        "source_repository": "pramodj551-oss/Part2-Cybersecurity-ML-Pipeline",
        "source_release_tag": "part2-runtime-33513838252",
        "source_release_commit": "4c7714cff07829d5fdcee052f936045df30c23b7",
        "bundle_name": "part2-runtime-bundle.zip",
        "bundle_sha256": "ece2b6bf91f19e5c0eb19475ae7198155f3fdaa4e8839ec9ab95f8cfcf031d54",
        "files": {path: _sha(path.encode()) for path in EXPECTED_ARTIFACTS},
    }


def _write_artifacts(root, manifest):
    for path, digest in manifest["files"].items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        data = path.encode()
        assert _sha(data) == digest
        target.write_bytes(data)


def test_valid_part3_handoff_contract():
    assert validate_handoff_manifest(_manifest()) is True


def test_provenance_mismatch_fails_closed():
    manifest = _manifest()
    manifest["source_release_commit"] = "0" * 64
    with pytest.raises(IntegrationContractError, match="source release commit"):
        validate_handoff_manifest(manifest)


def test_missing_manifest_fails_closed(tmp_path):
    with pytest.raises(IntegrationContractError, match="missing or empty"):
        load_handoff_manifest(tmp_path / "models" / "artifact_manifest.json")


def test_malformed_manifest_fails_closed(tmp_path):
    path = tmp_path / "artifact_manifest.json"
    path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(IntegrationContractError, match="valid JSON"):
        load_handoff_manifest(path)


def test_exact_six_file_schema_is_required():
    manifest = _manifest()
    manifest["files"]["unexpected.bin"] = "0" * 64
    with pytest.raises(IntegrationContractError, match="exactly the six"):
        validate_handoff_manifest(manifest)


def test_missing_or_empty_artifact_fails_closed(tmp_path):
    manifest = _manifest()
    _write_artifacts(tmp_path, manifest)
    (tmp_path / EXPECTED_ARTIFACTS[0]).unlink()
    with pytest.raises(IntegrationContractError, match="missing or empty"):
        validate_artifacts_against_manifest(tmp_path, manifest)


def test_tampered_artifact_hash_fails_closed(tmp_path):
    manifest = _manifest()
    _write_artifacts(tmp_path, manifest)
    target = tmp_path / EXPECTED_ARTIFACTS[1]
    target.write_bytes(b"tampered")
    with pytest.raises(IntegrationContractError, match="checksum mismatch"):
        validate_artifacts_against_manifest(tmp_path, manifest)


def test_artifact_manifest_json_round_trip(tmp_path):
    manifest = _manifest()
    path = tmp_path / "artifact_manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    loaded = load_handoff_manifest(path)
    assert validate_handoff_manifest(loaded) is True
