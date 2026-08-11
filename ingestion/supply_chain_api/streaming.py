from __future__ import annotations

"""
RetailFlow Supply Chain Kafka Streaming Ingestion.

Reads validated supply-chain orders from Kafka and converts
the JSON Kafka payload into a Spark Structured Streaming DataFrame.

Flow:

    Kafka: supply.orders
            ↓
    Spark Structured Streaming
            ↓
    Parsed Supply Order DataFrame
            ↓
    Bronze Delta

This module does not write to Bronze directly.
Bronze writing is centralized in BronzeWriter.
"""

import os

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from core.config import settings
from core.logger import get_logger
from core.spark_session import SparkSessionManager


logger = get_logger(__name__)


SUPPLY_ORDER_SCHEMA = StructType(
    [
        StructField("order_id", StringType(), False),
        StructField("supplier_id", StringType(), False),
        StructField("product_id", StringType(), False),
        StructField("quantity", IntegerType(), False),
        StructField("status", StringType(), False),
        StructField("order_timestamp", StringType(), False),
    ]
)


class SupplyChainStreamingPipeline:
    """
    Kafka → Spark Structured Streaming pipeline
    for supply-chain orders.
    """

    def __init__(self) -> None:
        self.spark = SparkSessionManager.get_session(
            app_name="RetailFlow-SupplyChain-Streaming"
        )

    def read_stream(self) -> DataFrame:
        """
        Read supply-chain orders from Kafka.

        Returns
        -------
        DataFrame
            Parsed Spark Structured Streaming DataFrame.
        """

        logger.info(
            "Reading Supply Chain Kafka stream..."
        )

        # --------------------------------------------------------------
        # Detect execution environment
        # --------------------------------------------------------------
        #
        # Windows:
        #     localhost:29092
        #
        # Docker:
        #     kafka:9092
        #
        # This prevents us from changing .env every time we switch
        # between Windows and Docker.
        # --------------------------------------------------------------

        running_in_docker = os.path.exists("/.dockerenv")

        if running_in_docker:
            kafka_bootstrap_servers = "kafka:9092"

            logger.info(
                "Detected Docker environment. "
                "Using Kafka: kafka:9092"
            )

        else:
            kafka_bootstrap_servers = (
                settings.kafka_bootstrap_servers
            )

            logger.info(
                "Detected local environment. "
                f"Using Kafka: {kafka_bootstrap_servers}"
            )

        # --------------------------------------------------------------
        # Kafka Structured Streaming source
        # --------------------------------------------------------------

        kafka_df = (
            self.spark.readStream
            .format("kafka")
            .option(
                "kafka.bootstrap.servers",
                kafka_bootstrap_servers,
            )
            .option(
                "subscribe",
                settings.kafka_supply_topic,
            )
            .option(
                "startingOffsets",
                "earliest",
            )
            .load()
        )

        logger.success(
            f"Connected to Kafka topic "
            f"'{settings.kafka_supply_topic}'."
        )

        # --------------------------------------------------------------
        # Parse Kafka JSON payload
        # --------------------------------------------------------------

        parsed_df = (
            kafka_df
            .selectExpr(
                "CAST(value AS STRING) AS value"
            )
            .select(
                from_json(
                    col("value"),
                    SUPPLY_ORDER_SCHEMA,
                ).alias("order")
            )
            .select("order.*")
        )

        return parsed_df