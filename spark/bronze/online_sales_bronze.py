"""
Bronze Layer

Reads streaming transactions from Kafka and writes them
to the Bronze layer without any transformations.
"""

from pyspark.sql.functions import col

from core.config import get_config
from core.logger import get_logger
from core.spark_session import get_spark_session

logger = get_logger(__name__)
config = get_config()


def read_online_sales():

    spark = get_spark_session(
        "Bronze-Online-Sales"
    )

    kafka_df = (
        spark.readStream
        .format("kafka")
        .option(
            "kafka.bootstrap.servers",
            ",".join(
                config.get(
                    "kafka",
                    "bootstrap_servers",
                )
            ),
        )
        .option(
            "subscribe",
            config.get(
                "kafka",
                "topics",
                "online_sales",
            ),
        )
        .option(
            "startingOffsets",
            "latest",
        )
        .load()
    )

    bronze_df = kafka_df.select(

        col("key").cast("string"),

        col("value").cast("string"),

        col("timestamp"),

        col("partition"),

        col("offset"),
    )

    query = (
        bronze_df.writeStream
        .format("delta")
        .option(
            "checkpointLocation",
            config.get(
                "storage",
                "checkpoints",
            )
            + "/online_sales",
        )
        .option(
            "path",
            config.get(
                "storage",
                "bronze",
            )
            + "/online_sales",
        )
        .outputMode("append")
        .start()
    )

    logger.info(
        "Bronze Streaming Started."
    )

    query.awaitTermination()


if __name__ == "__main__":

    read_online_sales()