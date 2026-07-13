"""
RetailFlow E-commerce Streaming Pipeline

Reads retail transactions from Kafka
and converts them into a Spark Streaming DataFrame.

This pipeline DOES NOT write data.

Responsibilities
----------------
✓ Read Kafka
✓ Parse JSON
✓ Apply Schema
✓ Return Streaming DataFrame
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    StructField,
    StructType,
    StringType,
    IntegerType,
    BooleanType,
)

from core.config import settings
from core.logger import get_logger
from core.spark_session import SparkSessionManager

logger = get_logger(__name__)


TRANSACTION_SCHEMA = StructType([

    StructField("transaction_id", StringType(), False),

    StructField("transaction_timestamp", StringType(), False),

    StructField("invoice_number", StringType(), False),

    StructField("store_id", StringType(), False),

    StructField("store_name", StringType(), False),

    StructField("country", StringType(), False),

    StructField("city", StringType(), False),

    StructField("region", StringType(), False),

    StructField("terminal_id", StringType(), False),

    StructField("cashier_id", StringType(), False),

    StructField("customer_id", StringType(), False),

    StructField("customer_segment", StringType(), True),

    StructField("loyalty_member", BooleanType(), True),

    StructField("product_id", StringType(), False),

    StructField("product_name", StringType(), False),

    StructField("category", StringType(), False),

    StructField("subcategory", StringType(), True),

    StructField("brand", StringType(), True),

    StructField("supplier_id", StringType(), True),

    StructField("quantity", IntegerType(), False),

    StructField("unit_price_cents", IntegerType(), False),

    StructField("discount_cents", IntegerType(), False),

    StructField("tax_cents", IntegerType(), False),

    StructField("total_amount_cents", IntegerType(), False),

    StructField("currency", StringType(), False),

    StructField("payment_method", StringType(), False),

    StructField("payment_provider", StringType(), True),

    StructField("promotion_id", StringType(), True),

    StructField("inventory_before", IntegerType(), True),

    StructField("inventory_after", IntegerType(), True),

    StructField("created_at", StringType(), False),
])


class EcommerceStreamingPipeline:

    """
    Kafka → Spark Structured Streaming
    """

    def __init__(self):

        self.spark = SparkSessionManager.get_session(
            app_name="RetailFlow-Streaming"
        )

    def read_stream(self) -> DataFrame:

        logger.info("Reading Kafka Stream...")

        kafka_df = (

            self.spark.readStream

            .format("kafka")

            .option(
                "kafka.bootstrap.servers",
                settings.kafka_bootstrap_servers,
            )

            .option(
                "subscribe",
                settings.kafka_transactions_topic,
            )

            .option(
                "startingOffsets",
                "latest",
            )

            .load()

        )

        logger.success("Kafka Stream Connected.")

        parsed_df = (

            kafka_df

            .selectExpr(
                "CAST(value AS STRING)"
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

        return parsed_df