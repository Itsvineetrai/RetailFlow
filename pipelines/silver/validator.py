"""
RetailFlow Silver Validator

Validates Bronze layer data before it is promoted
to the Silver layer.

Responsibilities
----------------
✓ Mandatory field validation
✓ Numeric validation
✓ Duplicate detection
✓ Split valid and invalid records
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from core.logger import get_logger

logger = get_logger(__name__)


class SilverValidator:

    """
    Validates Bronze DataFrame.
    """

    REQUIRED_COLUMNS = [
        "transaction_id",
        "transaction_timestamp",
        "store_id",
        "product_id",
        "quantity",
        "unit_price_cents",
        "total_amount_cents",
    ]

    def validate(self, df: DataFrame) -> tuple[DataFrame, DataFrame]:
        """
        Returns
        -------
        (valid_df, quarantine_df)
        """

        logger.info("Starting Silver Validation...")

        # --------------------------------------------------
        # Required fields
        # --------------------------------------------------

        valid_df = df

        for column in self.REQUIRED_COLUMNS:

            valid_df = valid_df.filter(
                col(column).isNotNull()
            )

        # --------------------------------------------------
        # Business Rules
        # --------------------------------------------------

        valid_df = (

            valid_df

            .filter(col("quantity") > 0)

            .filter(col("unit_price_cents") >= 0)

            .filter(col("discount_cents") >= 0)

            .filter(col("tax_cents") >= 0)

            .filter(col("total_amount_cents") >= 0)

        )

        # --------------------------------------------------
        # Remove duplicate transactions
        # --------------------------------------------------

        valid_df = valid_df.dropDuplicates(
            ["transaction_id"]
        )

        # --------------------------------------------------
        # Quarantine Records
        #
        # Anything that is NOT present in valid_df
        # based on transaction_id goes to quarantine.
        # --------------------------------------------------

        quarantine_df = (

            df.alias("bronze")

            .join(

                valid_df.alias("silver"),

                on="transaction_id",

                how="left_anti",

            )

        )

        logger.success("Validation completed.")

        logger.info(
            f"Valid Records      : {valid_df.count()}"
        )

        logger.info(
            f"Quarantined Records: {quarantine_df.count()}"
        )

        return valid_df, quarantine_df