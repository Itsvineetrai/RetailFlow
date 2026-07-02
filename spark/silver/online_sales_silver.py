"""
Silver Layer - Online Sales

Pipeline:
Bronze Delta
    ↓
Parse JSON
    ↓
Validate
    ↓
Currency Conversion
    ↓
Deduplicate
    ↓
Write Silver Delta
"""

from pyspark.sql.functions import col, from_json

from core.config import get_config
from core.logger import get_logger
from core.schemas import TRANSACTION_SCHEMA
from core.spark_session import get_spark_session

from spark.silver.validation import validate_transactions
from spark.silver.currency_conversion import apply_currency_conversion
from spark.silver.deduplication import remove_duplicates
from spark.silver.dlq_writer import write_dlq

logger = get_logger(__name__)
config = get_config()


def process_online_sales():

    spark = get_spark_session(
        "Silver-Online-Sales"
    )

    bronze_path = (
        config.get("storage", "bronze")
        + "/online_sales"
    )

    silver_path = (
        config.get("storage", "silver")
        + "/online_sales"
    )

    df = (
        spark.readStream
        .format("delta")
        .load(bronze_path)
    )

    parsed_df = (

        df

        .filter(
            col("value").isNotNull()
        )

        .select(

            from_json(
                col("value"),
                TRANSACTION_SCHEMA,
            ).alias("transaction")

        )

        .select(
            "transaction.*"
        )

    )

    # -----------------------------
    # Validation
    # -----------------------------

    valid_df, invalid_df = validate_transactions(
        parsed_df
    )

    # -----------------------------
    # Dead Letter Queue
    # -----------------------------

    write_dlq(
        invalid_df
    )

    # -----------------------------
    # Currency Conversion
    # -----------------------------

    valid_df = apply_currency_conversion(
        spark,
        valid_df,
    )

    # -----------------------------
    # Remove Duplicates
    # -----------------------------

    valid_df = remove_duplicates(
        valid_df
    )

    query = (

        valid_df

        .writeStream

        .format("delta")

        .option(

            "checkpointLocation",

            config.get(
                "storage",
                "checkpoints",
            )
            + "/silver_online_sales",

        )

        .outputMode("append")

        .start(
            silver_path
        )

    )

    logger.info(
        "Silver Layer Started."
    )

    query.awaitTermination()


if __name__ == "__main__":

    process_online_sales()