"""
RetailFlow Kafka Consumer

Consumes retail transactions from Kafka.

Flow

Kafka Topic
      ↓
Kafka Consumer
      ↓
Python Dictionary
"""

from __future__ import annotations

from core.config import settings
from core.kafka_client import KafkaClient
from core.logger import get_logger

logger = get_logger(__name__)


class TransactionConsumer:
    """
    Consumes retail transactions from Kafka.
    """

    def __init__(self):

        self.kafka = KafkaClient()

        self.consumer = self.kafka.create_consumer(
            topic=settings.kafka_transactions_topic,
            group_id="retailflow-consumer-group",
        )

    def consume(
        self,
        max_messages: int | None = None,
    ) -> None:
        """
        Consume Kafka messages.

        Parameters
        ----------
        max_messages : int | None
            Number of messages to consume.
            None means consume forever.
        """

        logger.info("Starting Kafka Consumer...")

        count = 0

        try:

            for message in self.consumer:

                transaction = message.value

                logger.info(
                    f"Transaction Received : "
                    f"{transaction['transaction_id']}"
                )

                logger.debug(transaction)

                count += 1

                if (
                    max_messages is not None
                    and count >= max_messages
                ):
                    break

        except KeyboardInterrupt:

            logger.warning(
                "Kafka Consumer stopped by user."
            )

        finally:

            self.close()

    def close(self):

        self.consumer.close()

        logger.info("Kafka Consumer closed.")


def main():

    consumer = TransactionConsumer()

    consumer.consume(
        max_messages=100,
    )


if __name__ == "__main__":
    main()