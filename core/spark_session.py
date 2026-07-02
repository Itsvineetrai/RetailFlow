"""
Central Spark Session for AeroMart.
Supports Delta Lake.
"""

from pyspark.sql import SparkSession

from core.config import get_config
from core.logger import get_logger

logger = get_logger(__name__)
config = get_config()


def get_spark_session(app_name: str) -> SparkSession:

    spark = (
        SparkSession.builder
        .appName(app_name)
        .master(config.get("spark", "master"))

        # Kafka
        .config(
            "spark.jars.packages",
            ",".join(
                [
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5",
                    "io.delta:delta-spark_2.12:3.2.1",
                    "org.apache.hadoop:hadoop-aws:3.3.4",
                    "com.amazonaws:aws-java-sdk-bundle:1.12.262",
                ]
            ),
        )
# -------------------------------------------------
# MinIO (S3A)
# -------------------------------------------------

        .config(
        "spark.hadoop.fs.s3a.endpoint",
        config.get(
            "minio",
            "endpoint",
        ),
        )

        .config(
            "spark.hadoop.fs.s3a.access.key",
        config.get(
            "minio",
            "access_key",
        ),
        )

        .config(
            "spark.hadoop.fs.s3a.secret.key",
        config.get(
            "minio",
            "secret_key",
        ),
        )

        .config(
            "spark.hadoop.fs.s3a.path.style.access",
            "true",
        )

        .config(
            "spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem",
        )

        .config(
            "spark.hadoop.fs.s3a.connection.ssl.enabled",
            "false",
        )

        # Delta Lake
        .config(
            "spark.sql.extensions",
            "io.delta.sql.DeltaSparkSessionExtension",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )

        # Performance
        .config(
            "spark.sql.adaptive.enabled",
            "true",
        )
        .config(
            "spark.sql.shuffle.partitions",
            "4",
        )
        .config(
            "spark.serializer",
            "org.apache.spark.serializer.KryoSerializer",
        )

        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    logger.info(
        "Spark Session '%s' started.",
        app_name,
    )

    return spark