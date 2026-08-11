from __future__ import annotations
import os
import sys

# -----------------------------------------------------------------------------
# Windows Native Hadoop Support
# -----------------------------------------------------------------------------
if os.name == "nt":
    hadoop_bin = r"C:\hadoop\bin"
    os.environ["HADOOP_HOME"] = r"C:\hadoop"
    os.environ["PATH"] = (
        hadoop_bin + os.path.pathsep + os.environ.get("PATH", "")
    )
    if sys.version_info >= (3, 8):
        try:
            os.add_dll_directory(hadoop_bin)
        except Exception:
            pass

from pyspark.sql import SparkSession
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


class SparkSessionManager:
    _spark: SparkSession | None = None

    @classmethod
    def get_session(
        cls,
        app_name: str = "RetailFlow",
    ) -> SparkSession:
        if cls._spark is None:
            logger.info("Creating Spark Session...")

            # ---------------------------------------------------------
            # Detect Runtime
            # ---------------------------------------------------------
            running_locally = (
                os.name == "nt" and not os.path.exists("/.dockerenv")
            )
            
            if running_locally:
                master_url = "local[*]"
                logger.info("Detected local Windows environment.")
            else:
                master_url = settings.spark_master
                logger.info(f"Connecting to Spark Master: {master_url}")

            # ---------------------------------------------------------
            # Create Session
            # ---------------------------------------------------------
            # S3A endpoint configuration must strictly omit the 'http://' prefix
            if running_locally:
                spark_endpoint = "localhost:9000"
            else:
                spark_endpoint = "minio:9000"

            logger.info(f"Connecting Hadoop S3A FileSystem to endpoint: {spark_endpoint}")

            builder = (
                SparkSession.builder
                .master(master_url)
                .appName(app_name)
                # ---------------------------------------------------------
                # Resource allocation
                # ---------------------------------------------------------
                .config(
                    "spark.cores.max",
                    "2",
                )
                .config(
                    "spark.executor.cores",
                    "1",
                )
                .config(
                    "spark.executor.memory",
                    "1g",
                )
 
                # --------------------------------------------
                # Local Filesystem & Dependency Packages
                # --------------------------------------------
                .config(
                    "spark.jars.packages",
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4,"
                    "org.apache.hadoop:hadoop-aws:3.3.4,"
                    "com.amazonaws:aws-java-sdk-bundle:1.12.262,"
                    "io.delta:delta-spark_2.12:3.2.0"
                )
                .config(
                    "spark.hadoop.fs.defaultFS",
                    "file:///",
                )
                .config(
                    "spark.hadoop.fs.interfaces.exception.on.permission.denied",
                    "false",
                )
                .config(
                    "spark.sql.extensions",
                    "io.delta.sql.DeltaSparkSessionExtension",
                )
                .config(
                    "spark.sql.catalog.spark_catalog",
                    "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                )
                # --------------------------------------------
                # MinIO (S3A) Configuration
                # --------------------------------------------
                .config(
                    "spark.hadoop.fs.s3a.endpoint",
                    spark_endpoint,
                )
                .config(
                    "spark.hadoop.fs.s3a.access.key",
                    settings.minio_access_key,
                )
                .config(
                    "spark.hadoop.fs.s3a.secret.key",
                    settings.minio_secret_key,
                )
                .config(
                    "spark.hadoop.fs.s3a.path.style.access",
                    "true",
                )
                .config(
                    "spark.hadoop.fs.s3a.connection.ssl.enabled",
                    "false",
                )
                .config(
                    "spark.hadoop.fs.s3a.impl",
                    "org.apache.hadoop.fs.s3a.S3AFileSystem",
                )
                .config(
                    "spark.delta.logStore.s3a.class",
                    "io.delta.storage.S3SingleDriverLogStore",
                )
                .config(
                    "spark.hadoop.fs.s3a.fast.upload",
                    "true",
                )
                .config(
                    "spark.hadoop.fs.s3a.fast.upload.buffer",
                    "array",
                )
            )

            cls._spark = builder.getOrCreate()
            cls._spark.sparkContext.setLogLevel("WARN")
            logger.success("Spark Session created successfully.")

        return cls._spark

    @classmethod
    def stop(cls) -> None:
        if cls._spark is not None:
            logger.info("Stopping Spark Session...")
            cls._spark.stop()
            cls._spark = None
            logger.success("Spark Session stopped.")
