"""
Project-wide constants for the AeroMart Data Platform.

Avoid hardcoding values throughout the codebase.
Import constants from this module instead.
"""

from decimal import Decimal

# Project

PROJECT_NAME = "AeroMart-DataPlatform"
BASE_CURRENCY = "USD"
TIMEZONE = "UTC"

# Kafka Topics

ONLINE_SALES_TOPIC = "online-sales"
DLQ_TOPIC = "dead-letter-queue"

# MinIO Buckets

RAW_BUCKET = "raw-pos-files"
BRONZE_BUCKET = "bronze"
SILVER_BUCKET = "silver"
GOLD_BUCKET = "gold"
DLQ_BUCKET = "dlq"
CHECKPOINT_BUCKET = "checkpoints"

# Storage Layers

BRONZE = "bronze"
SILVER = "silver"
GOLD = "gold"
DLQ = "dlq"

# Supported Currencies

SUPPORTED_CURRENCIES = (
    "USD",
    "EUR",
    "INR",
)

# Financial Precision

DECIMAL_PRECISION = Decimal("0.01")

# Data Quality

MAX_TRANSACTION_AMOUNT = Decimal("1000000.00")
MIN_TRANSACTION_AMOUNT = Decimal("0.01")

# Date Formats

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

# Logging

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)