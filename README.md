# 🛡️ AI-Powered Cybersecurity Incident Assistant (RAG)

Part 4 – End-to-End Applied AI & ML Capstone Project.

A Streamlit Retrieval-Augmented Generation assistant for cybersecurity incident investigation. The application retrieves trusted local knowledge, builds a security-aware prompt, and uses a local Ollama model through its OpenAI-compatible API.

## Current architecture

```text
Streamlit Chat
    ↓
Retriever → FAISS
    ↓
Retrieved documents (untrusted data)
    ↓
Prompt Builder
    ↓
LLMManager → Ollama / OpenAI-compatible API
    ↓
Answer + source names
```

Retrieved documents are treated as data, not instructions. Persisted FAISS metadata is loaded only after an externally supplied SHA-256 integrity check.

## Repository layout

```text
app.py
config/config.py
data/cybersecurity_incident_reports.csv
pages/Chat.py
pages/Incident_Search.py
pages/Knowledge_Base.py
pages/Settings.py
src/{data_loader,document_loader,embeddings,llm,prompt_builder,rag_pipeline,response_generator,retriever,text_splitter,utils,vector_store}.py
.github/workflows/{ci,dependency-review,python-publish}.yml
```

## Setup

Python 3.11 is the CI baseline.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Install and start Ollama separately, then make sure the model in `LLM_MODEL` exists locally. The default is `llama2`.

```bash
ollama pull llama2
ollama serve
streamlit run app.py
```

The authoritative incident dataset is `data/cybersecurity_incident_reports.csv`.

## Persisted FAISS index security

LangChain's local FAISS loader uses pickle for metadata. This project therefore refuses to load a persisted index unless `FAISS_INDEX_PKL_SHA256` exactly matches the SHA-256 of `vectorstore/faiss_index/index.pkl`.

After creating or receiving a trusted index, calculate its hash and set the environment variable before starting the application. Never accept a hash supplied by an untrusted source.

## Development and CI

Runtime dependencies are in `requirements.txt`; developer/CI-only tools are in `requirements-dev.txt`. `requirements.in` records the production dependency inputs. CI performs Python compilation, Ruff linting, pytest tests, pip-audit vulnerability checks, and a hashed pip-tools resolution check.

```bash
pip install -r requirements-dev.txt
pytest -q
ruff check app.py config src pages tests
```

## Important scope

The repository currently contains the application and incident CSV. External Part 1/2/3 repositories, generated model artifacts, and a persisted vector index are not assumed to exist in a fresh clone. Integration synchronization is therefore treated as an explicit deployment step rather than a hidden application dependency.

## License

MIT License.

## Author

Pramod Prakash Jadhav
