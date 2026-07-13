
"""
RetailFlow POS Batch Pipeline Runner

Runs the complete POS batch ingestion flow.

Usage:
    python scripts/run_pos_pipeline.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import get_logger
from ingestion.pos_batch.generator import POSBatchGenerator
from ingestion.pos_batch.pipeline import POSBatchPipeline

logger = get_logger(__name__)

OUTPUT_FILE = PROJECT_ROOT / "storage" / "landing" / "pos_transactions.csv"


def main() -> None:
    logger.info("=" * 70)
    logger.info("RetailFlow POS Batch Pipeline")
    logger.info("=" * 70)

    generator = POSBatchGenerator(seed=42)
    generator.to_csv(OUTPUT_FILE, records=1000)

    pipeline = POSBatchPipeline()
    dataframe = pipeline.run(OUTPUT_FILE)

    logger.info("Schema")
    dataframe.printSchema()

    logger.info("Sample Records")
    dataframe.show(10, truncate=False)

    total_records = dataframe.count()
    logger.success(f"Total Records: {total_records}")

    logger.success("POS Batch Pipeline completed successfully.")


if __name__ == "__main__":
    main()
