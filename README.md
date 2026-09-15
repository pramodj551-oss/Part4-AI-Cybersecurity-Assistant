# 🛡️ AI-Powered Cybersecurity Incident Assistant (RAG)

Part 4 – End-to-End Applied AI & ML Capstone Project.

A Streamlit Retrieval-Augmented Generation assistant for cybersecurity incident investigation. The application retrieves trusted local knowledge, builds a security-aware prompt, and uses an OpenAI-compatible LLM API to generate answers with source attribution.

## Production architecture

```text
User
  ↓
Streamlit Authentication
  ↓
Cybersecurity Chat
  ↓
Retriever → FAISS vector store
  ↓
Retrieved incident documents (data, not instructions)
  ↓
Security-aware Prompt Builder
  ↓
LLM Manager → OpenAI-compatible production API
  ↓
Answer + Sources
```

Production integrity boundary:
- Persisted FAISS metadata is accepted only after an externally supplied SHA-256 integrity check.
- Retrieved documents are treated as untrusted data, not executable instructions.
- Production credentials are supplied through Render environment secrets, never committed to the repository.

## Production / Go-Live evidence

**Status: Production Ready / Go-Live evidence complete.**

- Production service: `https://part4-ai-cybersecurity-api.onrender.com`
- Production health probe: `/_stcore/health` → HTTP 200 with healthy response.
- Authenticated controlled RAG smoke: successful answer with Sources; no secret/credential leakage observed.
- MEM-OPS-01: runtime memory-footprint mitigation merged and production stability smoke completed.
- PRA-01: Production Readiness audit completed.
- PRA-02: Operational contracts completed.
- PRA-03: Final production smoke and go-live evidence completed.

### Evidence discipline

Claims in this README are limited to evidence verified during the production-readiness workflow. GitHub Actions PASS is claimed only for specific verified workflow runs/commits; a commit without a recorded CI status is not presented as CI-green evidence.

## CI/CD evidence

Production-code mitigation evidence:
- PR #29: `https://github.com/pramodj551-oss/Part4-AI-Cybersecurity-Assistant/pull/29`
- Verified Actions run: `https://github.com/pramodj551-oss/Part4-AI-Cybersecurity-Assistant/actions/runs/34804110708`
- Production-code merge SHA: `3133b083e4f65c3ac5443b917e2470f26267afc2`

## Security evidence

- Environment-based authentication with PBKDF2-SHA256 password verification.
- No production password or password hash is committed to source control.
- FAISS `index.pkl` integrity is checked with SHA-256 before deserialization.
- RAG retrieved content is treated as data rather than instructions.
- CI includes linting, tests, dependency vulnerability auditing, and dependency-resolution checks.

## Resilience evidence

- Single-worker runtime configuration is used for constrained production resources.
- Embedding runtime uses CPU-only execution with constrained thread pools and `batch_size=1` to reduce transient memory pressure.
- Production smoke after the memory-footprint mitigation completed successfully without an observed new OOM/restart/502 in the validation window.
- Render Free tier exposes a 512 MB service limit but not measured application peak-memory telemetry; therefore no unsupported peak-memory number is claimed.

## Recruiter snapshot

**Role fit:** Applied AI/ML + Cybersecurity + Data/Threat Intelligence.

**What this project demonstrates:**
- End-to-end RAG architecture for cybersecurity incident investigation.
- Secure retrieval boundary with FAISS integrity verification.
- Environment-based authentication and secret hygiene.
- Production deployment and operational validation on Render.
- CI/CD quality gates and evidence-driven release discipline.
- Runtime resource hardening for a constrained deployment environment.

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

For local development, configure an OpenAI-compatible LLM endpoint and model in your local `.env`. Do not commit credentials.

The authoritative incident dataset is `data/cybersecurity_incident_reports.csv`.

## Streamlit sign-in

The application uses environment-based authentication. The documented default username is:

```text
Username: analyst
```

**There is intentionally no default production password in this repository.** A plaintext password committed to README, source code, or `.env.example` would expose a public credential and violate the production security model.

### Local development

Set `AUTH_USERNAME=analyst` and generate a password hash with the repository helper:

```bash
python scripts/generate_auth_hash.py
```

Store the generated value as `AUTH_PASSWORD_HASH` in your local `.env` file. Use the password you entered when generating the hash to sign in to the Streamlit application.

### Render production deployment

For the deployed application, configure production secrets only in the Render service environment/secret settings.

Do **not** put the production password, password hash, API keys, or other credentials in GitHub source files, README, issue comments, or screenshots.

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
