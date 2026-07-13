"""
RetailFlow POS Batch Pipeline

Pipeline Flow

CSV
 ↓
Reader
 ↓
Validator
 ↓
Return DataFrame
"""

from __future__ import annotations

from pathlib import Path

from pyspark.sql import DataFrame

from core.logger import get_logger

from ingestion.pos_batch.batch_reader import POSBatchReader
from ingestion.pos_batch.validator import POSBatchValidator

logger = get_logger(__name__)


class POSBatchPipeline:
    """
    End-to-end POS Batch Pipeline.
    """

    def __init__(self) -> None:

        self.reader = POSBatchReader()

        self.validator = POSBatchValidator()

    def run(
        self,
        file_path: str | Path,
    ) -> DataFrame:
        """
        Executes the complete batch pipeline.
        """

        logger.info("Starting POS Batch Pipeline")

        dataframe = self.reader.read_csv(file_path)

        self.validator.validate(dataframe)

        logger.success("POS Batch Pipeline completed.")

        return dataframe