"""
Bronze Layer - POS Batch Ingestion

Reads hourly POS CSV files from MinIO and stores them
in the Bronze Delta Layer.
"""

from pyspark.sql.functions import current_timestamp
from core.schemas import TRANSACTION_SCHEMA

from core.config import get_config
from core.logger import get_logger
from core.spark_session import get_spark_session

logger = get_logger(__name__)
config = get_config()


def ingest_pos_batches():

    spark = get_spark_session(
        "Bronze-POS-Ingestion"
    )

    raw_path = (
        "s3a://"
        + config.get(
            "minio",
            "buckets",
            "raw",
        )
        + "/*.csv"
    )

    bronze_path = (
        config.get(
            "storage",
            "bronze",
        )
        + "/pos_sales"
    )

    df = (
        spark.read
        .option("header", True)
        .schema(TRANSACTION_SCHEMA)
        .csv(raw_path)
    )

    bronze_df = df.withColumn(
        "ingestion_timestamp",
        current_timestamp(),
    )

    (
        bronze_df.write
        .format("delta")
        .mode("append")
        .save(bronze_path)
    )

    logger.info(
        "POS Bronze ingestion completed."
    )


if __name__ == "__main__":

    ingest_pos_batches()