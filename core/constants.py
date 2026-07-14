"""
RetailFlow Constants

This module contains project-wide constants that should never
change between environments.

Do NOT store secrets or configurable values here.
Use core.config for environment-specific settings.
"""

from __future__ import annotations

# =============================================================================
# PROJECT
# =============================================================================

PROJECT_NAME = "RetailFlow"

# =============================================================================
# STORAGE BUCKETS
# =============================================================================

MINIO_BUCKET = "retailflow"

# =============================================================================
# DATA LAKE PATHS
# =============================================================================

LANDING_PATH = f"s3a://{MINIO_BUCKET}/landing"

BRONZE_PATH = f"s3a://{MINIO_BUCKET}/bronze"

SILVER_PATH = f"s3a://{MINIO_BUCKET}/silver"

GOLD_PATH = f"s3a://{MINIO_BUCKET}/gold"

QUARANTINE_PATH = f"s3a://{MINIO_BUCKET}/quarantine"

ARCHIVE_PATH = f"s3a://{MINIO_BUCKET}/archive"

# =============================================================================
# DATASET PATHS
# =============================================================================

BRONZE_TRANSACTIONS_PATH = (
    f"{BRONZE_PATH}/transactions"
)

SILVER_TRANSACTIONS_PATH = (
    f"{SILVER_PATH}/transactions"
)

GOLD_TRANSACTIONS_PATH = (
    f"{GOLD_PATH}/transactions"
)

QUARANTINE_TRANSACTIONS_PATH = (
    f"{QUARANTINE_PATH}/transactions"
)

# =============================================================================
# CHECKPOINTS
# =============================================================================

CHECKPOINT_ROOT = (
    f"s3a://{MINIO_BUCKET}/checkpoints"
)

BRONZE_CHECKPOINT_PATH = (
    f"{CHECKPOINT_ROOT}/bronze"
)

SILVER_CHECKPOINT_PATH = (
    f"{CHECKPOINT_ROOT}/silver"
)

GOLD_CHECKPOINT_PATH = (
    f"{CHECKPOINT_ROOT}/gold"
)

# =============================================================================
# KAFKA
# =============================================================================

TRANSACTIONS_TOPIC = "retail.transactions"

# =============================================================================
# FILE FORMATS
# =============================================================================

PARQUET = "parquet"

CSV = "csv"

JSON = "json"

# =============================================================================
# PIPELINE MODES
# =============================================================================

APPEND = "append"

OVERWRITE = "overwrite"

# =============================================================================
# QUALITY
# =============================================================================

REQUIRED_TRANSACTION_COLUMNS = [
    "transaction_id",
    "transaction_timestamp",
    "store_id",
    "product_id",
    "quantity",
    "unit_price_cents",
    "total_amount_cents",
]