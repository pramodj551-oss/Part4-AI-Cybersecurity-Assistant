"""Build the FAISS index from the repository's authoritative incident CSV."""

from __future__ import annotations

import argparse

from langchain_core.documents import Document

from config.config import INCIDENT_DATASET, VECTOR_INDEX_PATH
from src.data_loader import data_loader
from src.vector_store import vector_store_manager


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(VECTOR_INDEX_PATH))
    args = parser.parse_args()

    dataframe = data_loader.load_csv(INCIDENT_DATASET)
    data_loader.validate(dataframe)

    documents = []
    for row_number, row in dataframe.fillna("").iterrows():
        fields = [f"{column}: {row[column]}" for column in dataframe.columns]
        documents.append(
            Document(
                page_content="\n".join(fields),
                metadata={"source": INCIDENT_DATASET.name, "row": int(row_number)},
            )
        )

    vector_store_manager.create(documents)
    digest = vector_store_manager.save(args.output)
    print(f"FAISS index created: {args.output}")
    print(f"index.pkl SHA-256: {digest}")


if __name__ == "__main__":
    main()
