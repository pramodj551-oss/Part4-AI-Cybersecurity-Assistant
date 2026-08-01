"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Document Loader
Version: 4.0
==========================================================

Loads unstructured documents for the RAG pipeline.
Supported Formats:
- PDF
- TXT
- Markdown
"""

from pathlib import Path
import logging

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader
)

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Load unstructured documents from files or folders.
    """

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".txt",
        ".md"
    }

    def load_document(self, file_path):
        """
        Load a single document.
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        suffix = file_path.suffix.lower()

        try:

            if suffix == ".pdf":

                loader = PyPDFLoader(
                    str(file_path)
                )

            elif suffix in {".txt", ".md"}:

                loader = TextLoader(
                    str(file_path),
                    encoding="utf-8"
                )

            else:

                raise ValueError(
                    f"Unsupported file type: {suffix}"
                )

            documents = loader.load()

            logger.info(
                "Loaded %s (%s chunks)",
                file_path.name,
                len(documents)
            )

            return documents

        except Exception as error:

            logger.exception(
                "Failed loading %s",
                file_path.name
            )

            raise error

    def load_directory(self, directory):
        """
        Load all supported documents from a directory.
        """

        directory = Path(directory)

        if not directory.exists():

            raise FileNotFoundError(
                f"Directory not found: {directory}"
            )

        documents = []

        for file in sorted(directory.rglob("*")):

            if (
                file.is_file()
                and file.suffix.lower()
                in self.SUPPORTED_EXTENSIONS
            ):

                documents.extend(
                    self.load_document(file)
                )

        logger.info(
            "Total documents loaded: %s",
            len(documents)
        )

        return documents

    def document_summary(
        self,
        documents
    ):
        """
        Return summary statistics.
        """

        return {

            "documents": len(documents),

            "characters": sum(
                len(doc.page_content)
                for doc in documents
            ),

            "metadata_entries": sum(
                len(doc.metadata)
                for doc in documents
            )

        }


document_loader = DocumentLoader()
