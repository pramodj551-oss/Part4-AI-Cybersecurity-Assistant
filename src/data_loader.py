"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Data Loader
Version: 4.0
==========================================================

Loads structured datasets (CSV) used by the RAG pipeline.
"""

from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


class DataLoader:
    """
    Utility class for loading structured datasets.
    """

    def __init__(self):

        self.dataframe = None

    def load_csv(self, file_path):
        """
        Load a CSV file.

        Parameters
        ----------
        file_path : str | Path

        Returns
        -------
        pandas.DataFrame
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )

        try:

            dataframe = pd.read_csv(file_path)

            logger.info(
                "Loaded CSV: %s",
                file_path.name
            )

            self.dataframe = dataframe

            return dataframe

        except Exception as error:

            logger.exception(
                "Failed loading CSV."
            )

            raise error

    def validate(self, dataframe):
        """
        Perform basic dataset validation.
        """

        if dataframe.empty:

            raise ValueError(
                "Dataset is empty."
            )

        duplicates = dataframe.duplicated().sum()

        missing = dataframe.isnull().sum().sum()

        logger.info(
            "Rows=%s Columns=%s Missing=%s Duplicates=%s",
            len(dataframe),
            len(dataframe.columns),
            int(missing),
            int(duplicates)
        )

        return {
            "rows": len(dataframe),
            "columns": len(dataframe.columns),
            "missing_values": int(missing),
            "duplicate_rows": int(duplicates)
        }

    def remove_duplicates(
        self,
        dataframe
    ):
        """
        Remove duplicate rows.
        """

        return dataframe.drop_duplicates()

    def remove_empty_rows(
        self,
        dataframe
    ):
        """
        Remove rows where every value is missing.
        """

        return dataframe.dropna(
            how="all"
        )

    def dataset_summary(
        self,
        dataframe
    ):
        """
        Return dataset summary.
        """

        return {

            "rows": len(dataframe),

            "columns": len(dataframe.columns),

            "column_names": list(
                dataframe.columns
            ),

            "data_types": dataframe.dtypes.astype(
                str
            ).to_dict()

        }


data_loader = DataLoader()
