"""
Main data generation pipeline for AeroMart.

Responsibilities
----------------
1. Generate continuous e-commerce transactions
2. Generate hourly POS transactions
3. Publish online sales to Kafka
4. Upload POS batch files to MinIO
"""

from __future__ import annotations

import time
import schedule
import threading
from datetime import datetime

from core.config import get_config
from core.logger import get_logger

from ingestion.ecommerce_generator import generate_transaction
from ingestion.batch.pos_generator import generate_pos_transaction
from ingestion.batch.csv_writer import CSVWriter
from ingestion.batch.minio_client import MinIOClient
from ingestion.producers.kafka_producer import KafkaProducerClient

logger = get_logger(__name__)

config = get_config()


def generate_pos_batch(batch_size: int = 100):

    writer = CSVWriter()

    minio = MinIOClient()

    transactions = [
        generate_pos_transaction()
        for _ in range(batch_size)
    ]

    filename = (
        f"pos_{datetime.now():%Y%m%d_%H%M%S}.csv"
    )

    csv_path = writer.write(
        transactions,
        filename,
    )

    minio.upload_file(
        bucket=config.get(
            "minio",
            "buckets",
            "raw",
        ),
        object_name=filename,
        file_path=str(csv_path),
    )

    logger.info(
        "Uploaded POS batch: %s",
        filename,
    )
    
def run_batch_scheduler():
    """
    Run POS batch generation on a schedule.
    """

    batch_interval = config.get(
        "generator",
        "batch_interval_minutes",
    )

    schedule.every(batch_interval).minutes.do(
        generate_pos_batch
    )

    logger.info(
        "POS Batch Scheduler Started."
    )

    while True:
        schedule.run_pending()
        time.sleep(1)


def stream_online_sales():

    producer = KafkaProducerClient()

    transactions_per_second = config.get(
        "generator",
        "transactions_per_second",
    )

    delay = 1 / transactions_per_second

    try:

        while True:

            transaction = generate_transaction()

            producer.publish(transaction)

            time.sleep(delay)

    except KeyboardInterrupt:

        producer.close()

        logger.info(
            "Streaming stopped."
        )


if __name__ == "__main__":

    scheduler_thread = threading.Thread(
        target=run_batch_scheduler,
        daemon=True,
    )

    scheduler_thread.start()

    stream_online_sales()