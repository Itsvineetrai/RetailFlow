"""
RetailFlow Constants

This module contains project-wide constants that should never
change between environments.

Do NOT store secrets or configurable values here.
Use core.config for environment-specific settings.
"""

from pathlib import Path

# =============================================================================
# Project Information
# =============================================================================

PROJECT_NAME = "RetailFlow"
PROJECT_VERSION = "1.0.0"

# =============================================================================
# Base Directories
# =============================================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = ROOT_DIR / "configs"

CORE_DIR = ROOT_DIR / "core"

INGESTION_DIR = ROOT_DIR / "ingestion"

STORAGE_DIR = ROOT_DIR / "storage"

LOG_DIR = ROOT_DIR / "logs"

TESTS_DIR = ROOT_DIR / "tests"

# =============================================================================
# Storage Paths
# =============================================================================

LANDING_DIR = STORAGE_DIR / "landing"

BRONZE_DIR = STORAGE_DIR / "bronze"

SILVER_DIR = STORAGE_DIR / "silver"

GOLD_DIR = STORAGE_DIR / "gold"

CHECKPOINT_DIR = STORAGE_DIR / "checkpoints"

QUARANTINE_DIR = STORAGE_DIR / "quarantine"

ARCHIVE_DIR = STORAGE_DIR / "archive"

# =============================================================================
# MinIO Buckets
# =============================================================================

LANDING_BUCKET = "landing"

BRONZE_BUCKET = "bronze"

SILVER_BUCKET = "silver"

GOLD_BUCKET = "gold"

# =============================================================================
# Kafka Topics
# =============================================================================

TRANSACTIONS_TOPIC = "retail.transactions"

INVENTORY_TOPIC = "inventory.updates"

SUPPLY_TOPIC = "supply.orders"

AUDIT_TOPIC = "audit.logs"

DLQ_TOPIC = "deadletter.transactions"

# =============================================================================
# Supported File Formats
# =============================================================================

CSV = "csv"

JSON = "json"

XML = "xml"

PARQUET = "parquet"

AVRO = "avro"

# =============================================================================
# Spark Application Names
# =============================================================================

SPARK_APP_BATCH = "RetailFlow-Batch"

SPARK_APP_STREAMING = "RetailFlow-Streaming"

SPARK_APP_RECONCILIATION = "RetailFlow-Reconciliation"

# =============================================================================
# Logging
# =============================================================================

DEFAULT_LOGGER_NAME = "RetailFlow"

DEFAULT_LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | "
    "{level:<8} | "
    "{name}:{function}:{line} | "
    "{message}"
)

# =============================================================================
# Time Formats
# =============================================================================

DEFAULT_TIMEZONE = "UTC"

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

DATE_FORMAT = "%Y-%m-%d"

# =============================================================================
# Retry Configuration
# =============================================================================

MAX_RETRIES = 3

RETRY_DELAY_SECONDS = 5

# =============================================================================
# Data Validation
# =============================================================================

SUPPORTED_POS_FILE_TYPES = (
    CSV,
    XML,
)

SUPPORTED_STREAM_FORMATS = (
    JSON,
    AVRO,
)

SUPPORTED_BATCH_FORMATS = (
    CSV,
    PARQUET,
)

# =============================================================================
# Exit Codes
# =============================================================================

SUCCESS = 0

FAILURE = 1