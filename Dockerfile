FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8502 \
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

EXPOSE 8502

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python scripts/healthcheck.py --health --port 8502

CMD ["streamlit", "run", "app.py", "--server.maxUploadSize=1024"]
