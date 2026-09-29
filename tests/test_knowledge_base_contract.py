"""Regression coverage for the Knowledge Base deployment contract."""

from pathlib import Path

from config.config import INCIDENT_DATASET


def test_knowledge_base_uses_authoritative_incident_dataset():
    page = Path("pages/Knowledge_Base.py").read_text(encoding="utf-8")

    assert "INCIDENT_DATASET" in page
    assert "data_loader.load_csv(INCIDENT_DATASET)" in page
    assert "Authoritative RAG source" in page


def test_missing_optional_knowledge_base_directory_is_not_a_page_failure():
    page = Path("pages/Knowledge_Base.py").read_text(encoding="utf-8")

    assert "if kb_path.is_dir():" in page
    assert 'st.warning("Knowledge base directory not found.")' not in page


def test_authoritative_incident_dataset_exists_for_the_standalone_contract():
    assert INCIDENT_DATASET.is_file()
