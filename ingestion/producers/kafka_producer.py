"""
Kafka Producer Client.
"""

from __future__ import annotations

from kafka import KafkaProducer

from core.config import get_config
from core.logger import get_logger

from .serializer import serialize


logger = get_logger(__name__)

config = get_config()


class KafkaProducerClient:

    def __init__(self):

        self.topic = config.get(
            "kafka",
            "topics",
            "online_sales",
        )

        self.producer = KafkaProducer(

            bootstrap_servers=config.get(
                "kafka",
                "bootstrap_servers",
            ),

            value_serializer=lambda x: x,
        )

        logger.info("Kafka Producer initialized.")

    def publish(self, transaction):

        self.producer.send(
            self.topic,
            serialize(transaction),
        )

        self.producer.flush()

        logger.info(
            "Transaction published: %s",
            transaction.transaction_id,
        )

    def close(self):

        self.producer.close()

        logger.info("Kafka Producer closed.")