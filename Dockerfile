FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    HF_HOME=/opt/huggingface

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --create-home app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.txt

COPY . .

# Build the production FAISS artifact from the tracked authoritative dataset.
# APP_ENVIRONMENT is forced to development only for image-build configuration
# validation; runtime production configuration remains explicit and fail-closed.
# PYTHONPATH is explicit because executing scripts/build_vectorstore.py sets
# sys.path[0] to /app/scripts rather than the repository root.
RUN mkdir -p /app/models /app/vectorstore /app/logs /opt/huggingface \
    && APP_ENVIRONMENT=development HF_HOME=/opt/huggingface PYTHONPATH=/app \
       python scripts/build_vectorstore.py --output /app/vectorstore/faiss_index \
    && sha256sum /app/vectorstore/faiss_index/index.pkl \
       > /app/vectorstore/faiss_index/index.pkl.sha256 \
    && chown -R app:app /app /opt/huggingface

USER app

# Render injects PORT at runtime (currently 10000). Keep 8502 as the local/default port.
EXPOSE 8502

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python scripts/healthcheck.py --health --port "${PORT:-8502}"

# Bind Streamlit to Render's injected PORT; fall back to 8502 for local/container use.
CMD ["sh", "-c", "exec streamlit run app.py --server.port=${PORT:-8502} --server.maxUploadSize=1024"]
