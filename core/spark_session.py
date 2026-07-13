"""
RetailFlow Spark Session Manager

Centralized SparkSession used throughout the project.

Supports
✓ Batch Processing
✓ Structured Streaming
✓ Kafka
✓ MinIO (S3A)
"""

from __future__ import annotations
import os
import sys

# ------------------------------------------------------------------
# FORCE WINDOWS NATIVE DLL COUPLING (No Admin Required)
# ------------------------------------------------------------------
if os.name == 'nt':
    hadoop_bin = "C:\\hadoop\\bin"
    os.environ["HADOOP_HOME"] = "C:\\hadoop"
    os.environ["PATH"] = hadoop_bin + os.path.pathsep + os.environ.get("PATH", "")
    
    # Force the Python memory context to trust and load the folder's DLLs
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

            # 1. DEFINE MASTER_URL: Automatically detect if running on local Windows or inside Docker
            is_windows_host = os.name == 'nt' and not os.path.exists('/.dockerenv')
            
            if is_windows_host:
                master_url = "local[*]"
                logger.info("Detected local Windows execution host. Using 'local[*]' engine fallback.")
            else:
                master_url = settings.spark_master  # Uses the variable from your .env
                logger.info(f"Detected cluster environment. Connecting to Master at: {master_url}")

            # 2. BUILD THE RUNTIME ENGINE WITH EXPLICIT WINDOWS SYSTEM FLAGS
            cls._spark = (
                SparkSession.builder
                .master(master_url)  
                .appName(app_name)
                
                .config(
                    "spark.jars.packages", 
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
                    "org.apache.spark:spark-token-provider-kafka-0-10_2.12:3.5.1,"
                    "org.apache.kafka:kafka-clients:3.5.1,"
                    "org.apache.hadoop:hadoop-aws:3.3.4,"
                    "com.amazonaws:aws-java-sdk-bundle:1.12.262"
                )
                # Tell Hadoop to bypass complex distributed file permission checks locally
                .config("spark.hadoop.fs.interfaces.exception.on.permission.denied", "false")
                # Direct local checkpoint threads to use standard local file protocols
                .config("spark.hadoop.fs.defaultFS", "file:///")
                
                .config("spark.hadoop.fs.s3a.fast.upload", "true")
                .config("spark.hadoop.fs.s3a.fast.upload.buffer", "array")
                # --------------------------------------------------
                # MinIO (S3A Storage Layer)
                # --------------------------------------------------
                .config(
                    "spark.hadoop.fs.s3a.endpoint",
                    settings.minio_endpoint,
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
                .getOrCreate()
            )

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
