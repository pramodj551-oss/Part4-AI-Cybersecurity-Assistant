"""Regression tests for low-memory embedding runtime safeguards."""


def test_embedding_runtime_limits_cpu_thread_pools_before_hf_import():
    source = open("src/embeddings.py", encoding="utf-8").read()

    hf_import = source.index("from langchain_huggingface import HuggingFaceEmbeddings")
    assert source.index('TOKENIZERS_PARALLELISM", "false"') < hf_import
    assert source.index('OMP_NUM_THREADS", "1"') < hf_import
    assert source.index('MKL_NUM_THREADS", "1"') < hf_import


def test_embedding_documents_use_single_item_batches():
    source = open("src/embeddings.py", encoding="utf-8").read()
    assert '"batch_size": 1' in source
