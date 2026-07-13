"""
RetailFlow Kafka Client

Centralized Kafka client for producers and consumers.

All Kafka communication in the project should go through
this module.

Author: RetailFlow
"""

from __future__ import annotations

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import json

from core.config import settings
from core.exceptions import (
    KafkaConnectionError,
    KafkaConsumerError,
    KafkaProducerError,
)
from core.logger import get_logger

logger = get_logger(__name__)


class KafkaClient:
    """
    Centralized Kafka Client.

    Creates Kafka producers and consumers with
    consistent configuration across the project.
    """

    def __init__(self) -> None:
        self.bootstrap_servers = settings.kafka_bootstrap_servers

    # ------------------------------------------------------------------
    # Producer
    # ------------------------------------------------------------------

    def create_producer(self) -> KafkaProducer:
        """
        Create a Kafka producer.
        """

        try:

            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                key_serializer=lambda key: (
                    key.encode("utf-8") if key else None
                ),
                retries=5,
                acks="all",
            )

            logger.success("Kafka Producer created.")

            return producer

        except KafkaError as exc:

            logger.exception("Failed to create Kafka Producer.")

            raise KafkaProducerError(str(exc)) from exc

        except Exception as exc:

            logger.exception("Kafka connection failed.")

            raise KafkaConnectionError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Consumer
    # ------------------------------------------------------------------

    def create_consumer(
        self,
        topic: str,
        group_id: str,
        auto_offset_reset: str = "earliest",
    ) -> KafkaConsumer:
        """
        Create a Kafka consumer.
        """

        try:

            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=True,
                value_deserializer=lambda value: json.loads(
                    value.decode("utf-8")
                ),
                key_deserializer=lambda key: (
                    key.decode("utf-8") if key else None
                ),
            )

            logger.success(
                f"Kafka Consumer subscribed to '{topic}'."
            )

            return consumer

        except KafkaError as exc:

            logger.exception("Failed to create Kafka Consumer.")

            raise KafkaConsumerError(str(exc)) from exc

        except Exception as exc:

            logger.exception("Kafka connection failed.")

            raise KafkaConnectionError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    def ping(self) -> bool:
        """
        Verify Kafka connectivity.
        """

        try:

            producer = self.create_producer()

            producer.bootstrap_connected()

            producer.close()

            logger.info("Kafka connection successful.")

            return True

        except Exception:

            logger.error("Kafka connection failed.")

            return False