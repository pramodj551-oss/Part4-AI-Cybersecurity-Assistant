from pathlib import Path


CHAT_PAGE = Path(__file__).resolve().parents[1] / "pages" / "Chat.py"


def test_chat_page_authenticates_before_heavy_rag_startup():
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert "from src.startup import initialize_vector_store" in source
    assert "require_auth()" in source
    assert "if not initialize_vector_store():" in source
    assert source.index("require_auth()") < source.index("if not initialize_vector_store():")
    assert source.index("if not initialize_vector_store():") < source.index("result = rag_pipeline.answer(question)")


def test_chat_page_defers_vector_store_initialization_until_question():
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert source.index("require_auth()") < source.index("question = st.chat_input")
    assert source.index("question = st.chat_input") < source.index("if question:")
    assert source.index("if question:") < source.index("initialize_vector_store()")
