from __future__ import annotations

from pyspark.sql import DataFrame

from core.constants import (
    APPEND,
    BRONZE_TRANSACTIONS_PATH,
)
from core.logger import get_logger

logger = get_logger(__name__)


class BronzeWriter:
    """
    Centralized writer for the Bronze Delta layer.

    Both streaming and batch ingestion should use this component
    so that Bronze write behavior is not duplicated.
    """

    def write_batch(
        self,
        dataframe: DataFrame,
    ) -> None:
        """
        Write a batch DataFrame to Bronze Delta.

        Data is appended because Bronze is an ingestion layer and
        should preserve incoming records.
        """

        logger.info(
            "Writing batch data to Bronze Delta..."
        )

        try:
            (
                dataframe.write
                .format("delta")
                .mode(APPEND)
                .save(BRONZE_TRANSACTIONS_PATH)
            )

            logger.success(
                "Batch data successfully written to Bronze Delta."
            )

        except Exception:
            logger.exception(
                "Failed to write batch data to Bronze Delta."
            )
            raise

    def write_stream(
        self,
        dataframe: DataFrame,
        checkpoint_path: str,
        trigger_interval: str = "10 seconds",
    ):
        """
        Write a streaming DataFrame to Bronze Delta.

        Returns the active StreamingQuery.
        """

        logger.info(
            "Starting streaming Bronze Delta writer..."
        )

        try:
            query = (
                dataframe.writeStream
                .format("delta")
                .outputMode(APPEND)
                .option(
                    "checkpointLocation",
                    checkpoint_path,
                )
                .option(
                    "path",
                    BRONZE_TRANSACTIONS_PATH,
                )
                .trigger(
                    processingTime=trigger_interval
                )
                .start()
            )

            logger.success(
                "Streaming Bronze Delta writer started."
            )

            return query

        except Exception:
            logger.exception(
                "Failed to start streaming Bronze Delta writer."
            )
            raise