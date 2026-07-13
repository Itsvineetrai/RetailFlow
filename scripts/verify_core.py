"""
RetailFlow Infrastructure Verification

Verifies the following services:

✓ Configuration
✓ Logger
✓ Spark
✓ Kafka
✓ MinIO

Usage:
    python scripts/verify_infrastructure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------
# Add project root to Python path
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from core.config import settings
from core.kafka_client import KafkaClient
from core.logger import get_logger
from core.minio_client import MinIOClient
from core.spark_session import SparkSessionManager

logger = get_logger(__name__)


def verify_config() -> bool:
    logger.info("Checking configuration...")

    logger.info(f"Project: {settings.project_name}")
    logger.info(f"Environment: {settings.environment}")

    return True


def verify_logger() -> bool:
    logger.info("Logger initialized successfully.")
    return True


def verify_spark() -> bool:
    logger.info("Checking Spark...")

    spark = SparkSessionManager.get_session(
        app_name="RetailFlow-Verification"
    )

    logger.success(
        f"Spark Version: {spark.version}"
    )

    SparkSessionManager.stop()

    return True


def verify_kafka() -> bool:
    logger.info("Checking Kafka...")

    kafka = KafkaClient()

    if kafka.ping():

        logger.success("Kafka connection successful.")

        return True

    return False


def verify_minio() -> bool:
    logger.info("Checking MinIO...")

    client = MinIOClient()

    buckets = client.list_buckets()

    logger.success(
        f"Connected to MinIO ({len(buckets)} buckets found)"
    )

    return True


def main() -> None:

    logger.info("=" * 60)
    logger.info("RetailFlow Infrastructure Verification")
    logger.info("=" * 60)

    checks = [
        ("Configuration", verify_config),
        ("Logger", verify_logger),
        ("Spark", verify_spark),
        ("Kafka", verify_kafka),
        ("MinIO", verify_minio),
    ]

    passed = 0

    for name, check in checks:

        try:

            if check():

                logger.success(f"{name:<20} PASSED")

                passed += 1

            else:

                logger.error(f"{name:<20} FAILED")

        except Exception as exc:

            logger.exception(exc)

            logger.error(f"{name:<20} FAILED")

    logger.info("-" * 60)
    logger.info(f"Passed {passed}/{len(checks)} checks")
    logger.info("-" * 60)

    if passed != len(checks):

        raise SystemExit(1)

    logger.success(
        "Infrastructure verification completed successfully."
    )


if __name__ == "__main__":
    main()