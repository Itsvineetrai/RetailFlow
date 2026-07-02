"""
Currency conversion using a Broadcast Join.

Since exchange_rates.csv is very small, Spark broadcasts it
to every executor, avoiding an expensive shuffle.
"""

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    broadcast,
    col,
)

from core.logger import get_logger

logger = get_logger(__name__)


def apply_currency_conversion(
    spark: SparkSession,
    transactions_df: DataFrame,
) -> DataFrame:
    """
    Convert transaction amounts to USD using
    a broadcast join with exchange rates.
    """

    exchange_rates_df = (

        spark.read

        .option("header", True)

        .csv("metadata/exchange_rates.csv")

        .withColumn(
            "rate_to_usd",
            col("rate_to_usd")
            .cast("decimal(18,6)")
        )

    )

    converted_df = (

        transactions_df.alias("transactions")

        .join(

            broadcast(exchange_rates_df).alias("rates"),

            col("transactions.currency")
            == col("rates.currency"),

            "left",

        )

        .withColumn(

            "amount_usd",

            (
                col("transactions.amount")
                * col("rates.rate_to_usd")
            ).cast("decimal(18,2)")

        )

        .drop(
            "rates.currency",
            "rate_to_usd",
            "effective_date",
        )

    )

    logger.info(
        "Currency conversion completed using Broadcast Join."
    )

    return converted_df