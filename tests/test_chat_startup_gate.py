from pathlib import Path


CHAT_PAGE = Path(__file__).resolve().parents[1] / "pages" / "Chat.py"


def test_chat_page_initializes_verified_startup_before_rag_pipeline():
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert "from src.startup import check_startup" in source
    assert "if not check_startup():" in source
    assert "st.error(\"The assistant is not ready: required startup dependencies are unavailable.\")" in source
    assert source.index("if not check_startup():") < source.index("from src.rag_pipeline import rag_pipeline")
