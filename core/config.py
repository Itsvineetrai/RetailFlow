"""
RetailFlow Configuration

Loads all application settings from the .env file.

Usage:
    from core.config import settings

    print(settings.kafka_bootstrap_servers)
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ------------------------------------------------------------------
# Load .env
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR.parent / ".env"

load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    """
    Central configuration for the RetailFlow platform.
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ==========================================================
    # Project
    # ==========================================================

    project_name: str = Field(default="RetailFlow", alias="PROJECT_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # ==========================================================
    # Kafka
    # ==========================================================

    kafka_bootstrap_servers: str = Field(
        default="localhost:29092",
        alias="KAFKA_BOOTSTRAP_SERVERS",
    )

    kafka_transactions_topic: str = Field(
        default="retail.transactions",
        alias="KAFKA_TOPIC_TRANSACTIONS",
    )

    kafka_inventory_topic: str = Field(
        default="inventory.updates",
        alias="KAFKA_TOPIC_INVENTORY",
    )

    kafka_supply_topic: str = Field(
        default="supply.orders",
        alias="KAFKA_TOPIC_SUPPLY",
    )

    # ==========================================================
    # Spark
    # ==========================================================

    spark_master: str = Field(
        default="spark://spark-master:7077",
        alias="SPARK_MASTER",
    )

    spark_driver_memory: str = Field(
        default="2g",
        alias="SPARK_DRIVER_MEMORY",
    )

    spark_executor_memory: str = Field(
        default="2g",
        alias="SPARK_EXECUTOR_MEMORY",
    )

    spark_executor_cores: int = Field(
        default=2,
        alias="SPARK_EXECUTOR_CORES",
    )

    # ==========================================================
    # MinIO
    # ==========================================================

    minio_endpoint: str = Field(
        default="localhost:9000",
        alias="MINIO_ENDPOINT",
    )

    minio_access_key: str = Field(
        default="minioadmin",
        alias="MINIO_ROOT_USER",
    )

    minio_secret_key: str = Field(
        default="minioadmin",
        alias="MINIO_ROOT_PASSWORD",
    )

    minio_bucket: str = Field(
        default="landing",
        alias="MINIO_BUCKET",
    )

    # ==========================================================
    # PostgreSQL
    # ==========================================================

    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")

    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    postgres_db: str = Field(default="airflow", alias="POSTGRES_DB")

    postgres_user: str = Field(default="airflow", alias="POSTGRES_USER")

    postgres_password: str = Field(
        default="airflow",
        alias="POSTGRES_PASSWORD",
    )

    # ==========================================================
    # Airflow
    # ==========================================================

    airflow_url: str = Field(
        default="http://localhost:8088",
        alias="AIRFLOW_URL",
    )

    # ==========================================================
    # Logging
    # ==========================================================

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )


settings = Settings()