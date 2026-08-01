"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Text Splitter
Version: 4.0
==========================================================

Splits LangChain documents into smaller chunks while
preserving metadata for retrieval.
"""

import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE
)

logger = logging.getLogger(__name__)


class TextSplitter:
    """
    Production-ready text splitter.
    """

    def __init__(
        self,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    ):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def split_documents(
        self,
        documents
    ):
        """
        Split LangChain documents.
        """

        if not documents:

            logger.warning(
                "No documents supplied."
            )
            return []

        chunks = self.splitter.split_documents(
            documents
        )

        logger.info(
            "Generated %s chunks.",
            len(chunks)
        )

        return chunks

    def split_text(
        self,
        text,
        metadata=None
    ):
        """
        Split a single text string.
        """

        if metadata is None:
            metadata = {}

        document = Document(
            page_content=text,
            metadata=metadata
        )

        return self.split_documents(
            [document]
        )

    def chunk_statistics(
        self,
        chunks
    ):
        """
        Return chunk statistics.
        """

        if not chunks:

            return {
                "chunks": 0,
                "average_length": 0,
                "max_length": 0,
                "min_length": 0
            }

        lengths = [
            len(chunk.page_content)
            for chunk in chunks
        ]

        return {

            "chunks": len(chunks),

            "average_length": round(
                sum(lengths) / len(lengths),
                2
            ),

            "max_length": max(lengths),

            "min_length": min(lengths)

        }


text_splitter = TextSplitter()
