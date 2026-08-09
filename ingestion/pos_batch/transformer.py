from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from core.logger import get_logger

logger = get_logger(__name__)


class POSBatchTransformer:
    """
    Normalizes POS batch data to the existing Bronze Delta schema.

    Bronze is an ingestion layer, so business transformations are
    intentionally kept out of this component.

    Important:
        The existing Bronze Delta contract stores timestamp fields
        as strings. POS batch data must therefore conform to that
        schema before being appended.
    """

    TIMESTAMP_COLUMNS = [
        "transaction_timestamp",
        "created_at",
    ]

    @classmethod
    def transform(
        cls,
        dataframe: DataFrame,
    ) -> DataFrame:
        """
        Normalize POS batch data for Bronze ingestion.
        """

        logger.info(
            "Transforming POS batch DataFrame..."
        )

        transformed = dataframe

        # ------------------------------------------------------------------
        # Bronze schema compatibility
        # ------------------------------------------------------------------
        #
        # The existing Bronze Delta table stores these fields as STRING.
        #
        # Spark CSV inference may produce TIMESTAMP columns for these
        # fields. Explicitly cast them back to STRING so that batch
        # ingestion conforms to the existing Bronze contract.
        #
        # Business-level timestamp normalization belongs in Silver.
        # ------------------------------------------------------------------

        for column_name in cls.TIMESTAMP_COLUMNS:

            if column_name in transformed.columns:

                transformed = transformed.withColumn(
                    column_name,
                    col(column_name).cast("string"),
                )

        logger.success(
            "POS batch transformation completed."
        )

        return transformed