"""
RetailFlow POS Batch Validator

Validates incoming POS batch data before loading it
into the Landing/Bronze layer using high-performance native Spark functions.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from core.logger import get_logger
from core.exceptions import ValidationError

logger = get_logger(__name__)


class POSBatchValidator:
    """
    Performs basic validation on POS batch files.
    """

    REQUIRED_COLUMNS = [
        "transaction_id",
        "store_id",
        "terminal_id",
        "product_id",
        "quantity",
        "total_amount_cents",
        "transaction_timestamp",
    ]

    @classmethod
    def validate_columns(cls, dataframe: DataFrame) -> None:
        """
        Validate required columns exist.
        """
        dataframe_columns = set(dataframe.columns)

        missing_columns = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in dataframe_columns
        ]

        if missing_columns:
            logger.error(
                f"Missing required columns: {missing_columns}"
            )
            raise ValidationError(
                f"Missing columns: {missing_columns}"
            )

        logger.success("Column validation passed.")

    @staticmethod
    def validate_empty_dataframe(dataframe: DataFrame) -> None:
        """
        Ensure DataFrame is not empty using high-performance native optimization.
        """
        # FIX: Replacing dataframe.rdd.isEmpty() with a native head(1) evaluation.
        # head(1) retrieves exactly one item purely within memory, bypassing 
        # Python serialization wrappers entirely and avoiding Windows worker crashes.
        if not dataframe.head(1):
            logger.error("Input DataFrame is empty.")
            raise ValidationError(
                "Input DataFrame is empty."
            )

        logger.success("DataFrame contains records.")

    @staticmethod
    def validate_duplicate_transactions(
        dataframe: DataFrame,
    ) -> None:
        """
        Detect duplicate transaction IDs.
        """
        duplicate_count = (
            dataframe.groupBy("transaction_id")
            .count()
            .filter(col("count") > 1)
            .count()
        )

        if duplicate_count > 0:
            logger.warning(
                f"Duplicate transactions detected: {duplicate_count}"
            )
        else:
            logger.success(
                "No duplicate transaction IDs found."
            )

    @classmethod
    def validate(
        cls,
        dataframe: DataFrame,
    ) -> None:
        """
        Execute all validations.
        """
        logger.info("Starting POS batch validation...")

        cls.validate_empty_dataframe(dataframe)
        cls.validate_columns(dataframe)
        cls.validate_duplicate_transactions(dataframe)

        logger.success("POS batch validation completed.")
