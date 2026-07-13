"""
RetailFlow Kafka Producer

Produces retail transactions to Kafka.

Flow

Transaction Generator
        ↓
Kafka Producer
        ↓
Kafka Topic
"""

from __future__ import annotations

import time

from core.config import settings
from core.kafka_client import KafkaClient
from core.logger import get_logger

from ingestion.pos_batch.generator import POSBatchGenerator

logger = get_logger(__name__)


class TransactionProducer:
    """
    Produces retail transactions to Kafka.
    """

    def __init__(self):

        self.kafka = KafkaClient()

        self.producer = self.kafka.create_producer()

        self.generator = POSBatchGenerator(seed=42)

        self.topic = settings.kafka_transactions_topic

    def send_transaction(
        self,
        transaction: dict,
    ) -> None:
        """
        Send one transaction.
        """

        try:

            future = self.producer.send(
                self.topic,
                value=transaction,
                key=transaction["transaction_id"],
            )

            future.get(timeout=10)

            logger.success(
                f"Transaction {transaction['transaction_id']} sent."
            )

        except Exception as exc:

            logger.exception(exc)

    def send_transactions(
        self,
        count: int = 100,
        delay: float = 0.1,
    ) -> None:
        """
        Produce multiple transactions.
        """

        logger.info(
            f"Producing {count} transactions..."
        )

        transactions = self.generator.generate(count)

        for transaction in transactions:

            self.send_transaction(transaction)

            time.sleep(delay)

        self.producer.flush()

        logger.success(
            "All transactions published."
        )

    def close(self):

        self.producer.close()

        logger.info("Kafka Producer closed.")


def main():

    producer = TransactionProducer()

    producer.send_transactions(
        count=100,
        delay=0.05,
    )

    producer.close()


if __name__ == "__main__":
    main()