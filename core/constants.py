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

POS_BATCH_INPUT_PATH = (
    f"{LANDING_PATH}/pos/pos_transactions.csv"
)

BRONZE_TRANSACTIONS_PATH = (
    f"{BRONZE_PATH}/transactions"
)

SILVER_TRANSACTIONS_PATH = (
    f"{SILVER_PATH}/transactions"
)
SILVER_FORECASTING_PATH = (
    f"{SILVER_PATH}/forecasting_history"
)

GOLD_DAILY_DEMAND_PATH = (
    f"{GOLD_PATH}/daily_demand"
)

GOLD_FORECASTING_DATASET_PATH = (
    f"{GOLD_PATH}/forecasting_dataset"
)

GOLD_TRANSACTIONS_PATH = (
    f"{GOLD_PATH}/transactions"
)

QUARANTINE_TRANSACTIONS_PATH = (
    f"{QUARANTINE_PATH}/transactions"
) 

BRONZE_SUPPLY_ORDERS_PATH = (
    f"{BRONZE_PATH}/supply_orders"
)

HISTORICAL_FORECASTING_PATH = (
    f"{LANDING_PATH}/pos/historical_pos_180d.csv"
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

TRANSACTIONS_CHECKPOINT_PATH = (
    f"{CHECKPOINT_ROOT}/transactions"
)

SILVER_CHECKPOINT_PATH = (
    f"{CHECKPOINT_ROOT}/silver"
)

GOLD_CHECKPOINT_PATH = (
    f"{CHECKPOINT_ROOT}/gold"
)

SUPPLY_ORDERS_CHECKPOINT_PATH = (
    f"{CHECKPOINT_ROOT}/supply_orders"
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