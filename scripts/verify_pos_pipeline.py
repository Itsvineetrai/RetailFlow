"""
RetailFlow POS Pipeline Verification

Verifies the complete POS batch ingestion pipeline.

Checks:
✓ Landing file exists
✓ File is readable
✓ DataFrame is not empty
✓ Required columns exist
✓ No duplicate transaction IDs
✓ Pipeline executes successfully

Usage:
    python scripts/verify_pos_pipeline.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import get_logger
from ingestion.pos_batch.pipeline import POSBatchPipeline
from core.spark_session import SparkSessionManager

logger = get_logger(__name__)

CSV_FILE = (
    PROJECT_ROOT
    / "storage"
    / "landing"
    / "pos_transactions.csv"
)

REQUIRED_COLUMNS = [
    "transaction_id",
    "transaction_timestamp",
    "store_id",
    "product_id",
    "quantity",
    "unit_price_cents",
    "discount_cents",
    "tax_cents",
    "total_amount_cents",
]


def verify_file_exists():
    logger.info("Checking landing file...")
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"Landing file not found at: {CSV_FILE}")
    logger.success("Landing file found.")


def verify_pipeline():
    logger.info("Running POS Pipeline...")
    pipeline = POSBatchPipeline()
    
    # Pass the clean string representation or path to the pipeline wrapper
    df = pipeline.run(CSV_FILE)
    logger.success("Pipeline executed successfully.")
    return df


def verify_row_count(df):
    rows = df.count()
    if rows == 0:
        raise ValueError("CSV contains zero records.")
    logger.success(f"Record Count : {rows}")


def verify_columns(df):
    missing = []
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            missing.append(column)

    if missing:
        raise ValueError(
            f"Missing columns: {missing}. Available columns: {df.columns}"
        )
    logger.success("Required columns verified.")


def verify_duplicates(df):
    duplicate_count = (
        df.groupBy("transaction_id")
        .count()
        .filter("count > 1")
        .count()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"Duplicate Transaction IDs detected: {duplicate_count}"
        )
    logger.success("No duplicate transaction IDs.")


def main():
    logger.info("=" * 70)
    logger.info("RetailFlow POS Pipeline Verification")
    logger.info("=" * 70)

    try:
        verify_file_exists()
        dataframe = verify_pipeline()

        if dataframe is not None:
            verify_row_count(dataframe)
            verify_columns(dataframe)
            verify_duplicates(dataframe)
            
            logger.info("Previewing loaded pipeline records:")
            dataframe.show(5, truncate=False)

            logger.info("=" * 70)
            logger.success("POS PIPELINE VERIFICATION PASSED")
            logger.info("=" * 70)
        else:
            raise ValueError("Pipeline run returned an empty or None DataFrame object.")

    except Exception as e:
        logger.error(f"Verification stopped due to an explicit crash: {str(e)}")
        raise e
        
    finally:
        # Protect lifecycle: Shut down the cluster context gracefully only when exiting main()
        logger.info("Cleaning up pipeline active tracking contexts...")
        try:
            spark = SparkSessionManager.get_session("RetailFlow-POS-Reader")
            spark.stop()
            logger.success("Spark Session dropped cleanly.")
        except Exception as cleanup_err:
            logger.info(f"Background cluster stopped cleanly: {cleanup_err}")


if __name__ == "__main__":
    main()
