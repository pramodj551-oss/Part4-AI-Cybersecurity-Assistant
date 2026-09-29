"""Interactive cybersecurity RAG chat page."""

import time
import uuid

import streamlit as st

from config.config import APP_ICON
from src.auth import render_logout, require_auth
from src.startup import initialize_vector_store

st.set_page_config(
    page_title="Chat",
    page_icon=APP_ICON,
    layout="wide",
)

# Authentication is deliberately evaluated before FAISS/embedding/LLM initialization.
# The heavy production vector-store startup and OpenAI-compatible client creation
# are deferred until the first authenticated chat request.
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
    request_id = uuid.uuid4().hex[:12]
    request_started = time.monotonic()
    print(f"CHAT_PROBE: request_start request_id={request_id}", flush=True)
    st.session_state.chat_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving relevant context and generating response..."):
            try:
                with st.spinner("Preparing the verified cybersecurity knowledge base..."):
                    print(f"CHAT_PROBE: startup_initialization_start request_id={request_id}", flush=True)
                    startup_started = time.monotonic()
                    if not initialize_vector_store():
                        raise RuntimeError("Production startup checks failed; the assistant is not ready.")
                    print(f"CHAT_PROBE: startup_initialization_done request_id={request_id} elapsed_ms={int((time.monotonic()-startup_started)*1000)}", flush=True)

                # Import only after authentication and verified vector-store initialization.
                # src.llm constructs its OpenAI-compatible client at import time.
                from src.rag_pipeline import rag_pipeline

                print(f"CHAT_PROBE: rag_request_start request_id={request_id}", flush=True)
                rag_started = time.monotonic()
                result = rag_pipeline.answer(question, request_id=request_id)
                print(f"CHAT_PROBE: rag_request_done request_id={request_id} elapsed_ms={int((time.monotonic()-rag_started)*1000)}", flush=True)
                answer = result.get("answer") or "No answer was generated."
                sources = result.get("sources", [])
            except (ValueError, FileNotFoundError, RuntimeError) as error:
                print(f"CHAT_PROBE: request_error request_id={request_id} exception={type(error).__name__}", flush=True)
                answer = f"The assistant is not ready: {error}"
                sources = []
            except Exception as error:
                print(f"CHAT_PROBE: request_error request_id={request_id} exception={type(error).__name__}", flush=True)
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
