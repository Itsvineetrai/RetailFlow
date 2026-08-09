from __future__ import annotations

from pathlib import Path

from pyspark.sql import DataFrame

from core.logger import get_logger
from ingestion.pos_batch.batch_reader import POSBatchReader
from ingestion.pos_batch.transformer import POSBatchTransformer
from ingestion.pos_batch.validator import POSBatchValidator
from pipelines.bronze.bronze_writer import BronzeWriter

logger = get_logger(__name__)


class POSBatchPipeline:
    """
    End-to-end POS Batch ingestion pipeline.

    Flow:

        Input File
            ↓
        Reader
            ↓
        Validator
            ↓
        Transformer
            ↓
        Bronze Delta
    """

    def __init__(self) -> None:

        self.reader = POSBatchReader()

        self.validator = POSBatchValidator()

        self.transformer = POSBatchTransformer()

        self.bronze_writer = BronzeWriter()

    def run(
        self,
        file_path: str | Path,
    ) -> DataFrame:
        """
        Execute the complete POS batch ingestion pipeline.

        Parameters
        ----------
        file_path:
            CSV, JSON, or Parquet input file.

        Returns
        -------
        DataFrame
            The transformed DataFrame that was written to Bronze.
        """

        logger.info(
            f"Starting POS Batch Pipeline: {file_path}"
        )

        # --------------------------------------------------------------
        # 1. Read
        # --------------------------------------------------------------

        dataframe = self.reader.read(file_path)

        logger.info(
            f"Input columns: {dataframe.columns}"
        )

        # --------------------------------------------------------------
        # 2. Validate
        # --------------------------------------------------------------

        self.validator.validate(dataframe)

        # --------------------------------------------------------------
        # 3. Transform
        # --------------------------------------------------------------

        dataframe = self.transformer.transform(
            dataframe
        )

        # --------------------------------------------------------------
        # 4. Write Bronze
        # --------------------------------------------------------------

        self.bronze_writer.write_batch(
            dataframe
        )

        logger.success(
            "POS Batch Pipeline completed successfully."
        )

        return dataframe