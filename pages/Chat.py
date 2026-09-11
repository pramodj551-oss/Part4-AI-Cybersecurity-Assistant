"""Interactive cybersecurity RAG chat page."""

import streamlit as st

from config.config import APP_ICON
from src.auth import render_logout, require_auth
from src.startup import check_startup
from src.rag_pipeline import rag_pipeline

st.set_page_config(
    page_title="Chat",
    page_icon=APP_ICON,
    layout="wide",
)

# Streamlit multipage navigation can execute this page directly. Therefore the
# Chat entrypoint must enforce the same verified production startup gate as the
# home page before exposing the RAG pipeline.
if not check_startup():
    st.error("The assistant is not ready: required startup dependencies are unavailable.")
    st.stop()

require_auth()
render_logout()

st.title("💬 Cybersecurity AI Assistant")
st.caption("Answers are grounded in retrieved cybersecurity knowledge. Untrusted document text is never treated as an instruction.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

with st.sidebar:
    st.header("AI Cybersecurity Assistant")
    st.success("Ready")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

question = st.chat_input("Ask a cybersecurity question...")

if question:
    st.session_state.chat_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving relevant context and generating response..."):
            try:
                result = rag_pipeline.answer(question)
                answer = result.get("answer") or "No answer was generated."
                sources = result.get("sources", [])
            except (ValueError, FileNotFoundError, RuntimeError) as error:
                answer = f"The assistant is not ready: {error}"
                sources = []
            except Exception:
                answer = "The assistant could not complete the request. Check the application logs for details."
                sources = []

        st.markdown(answer)
        if sources:
            with st.expander("Sources"):
                for source in sources:
                    st.write(f"- {source}")

    st.session_state.chat_messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
