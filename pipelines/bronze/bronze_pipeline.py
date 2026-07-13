"""
RetailFlow Bronze Pipeline

Reads streaming transactions from the
EcommerceStreamingPipeline and writes
them into the Bronze layer inside MinIO.

Flow

Kafka
    ↓
Spark Streaming
    ↓
Bronze (Parquet inside MinIO)
"""

from __future__ import annotations

from core.logger import get_logger
from ingestion.ecommerce_stream.pipeline import (
    EcommerceStreamingPipeline,
)

logger = get_logger(__name__)


class BronzePipeline:

    def __init__(self):
        self.pipeline = EcommerceStreamingPipeline()

    def start(self):
        logger.info("Starting Bronze Pipeline...")

        # 1. READ FRESH STREAM FROM KAFKA
        stream_df = self.pipeline.read_stream()

        # 2. DEFINE S3A CLOUD STORAGE PATHS (Bypasses broken Windows local file checks entirely!)
        # Note: Change 'retailflow' to your actual target MinIO bucket name if it is different
        bucket_name = "retailflow" 
        
        s3_checkpoint = f"s3a://{bucket_name}/checkpoints/bronze"
        s3_output = f"s3a://{bucket_name}/bronze/transactions"

        # 3. CONFIGURE STREAM WRITER TARGETING MINIO BUCKET CONTEXTS
        query = (
            stream_df.writeStream
            .format("parquet")
            .option(
                "checkpointLocation",
                s3_checkpoint,
            )
            .option(
                "path",
                s3_output,
            )
            .outputMode("append")
            .start()
        )

        logger.success(
            "Bronze Pipeline Started."
        )

        query.awaitTermination()


def main():
    BronzePipeline().start()


if __name__ == "__main__":
    main()
