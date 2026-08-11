"""
RetailFlow Supply Chain API Ingestion Pipeline.

Flow:

REST API
    ↓
API Client
    ↓
Validator
    ↓
Kafka
    ↓
supply.orders
"""

from __future__ import annotations

from typing import Any

from core.config import settings
from core.kafka_client import KafkaClient
from core.logger import get_logger
from ingestion.supply_chain_api.client import (
    SupplyChainAPIClient,
)
from ingestion.supply_chain_api.validator import (
    SupplyChainAPIValidator,
)

logger = get_logger(__name__)


class SupplyChainAPIPipeline:
    """
    End-to-end Supply Chain API ingestion pipeline.
    """

    def __init__(self) -> None:

        self.client = SupplyChainAPIClient()

        self.validator = SupplyChainAPIValidator()

        self.kafka_client = KafkaClient()

    def run(self) -> int:
        """
        Fetch, validate and publish Supply Chain records.

        Returns
        -------
        int
            Number of valid records published.
        """

        logger.info(
            "Starting Supply Chain API ingestion..."
        )

        records = self.client.fetch_orders()

        valid_records, invalid_records = (
            self.validator.validate_records(records)
        )

        if invalid_records:

            logger.warning(
                f"{len(invalid_records)} invalid "
                "Supply Chain records detected."
            )

        if not valid_records:

            logger.warning(
                "No valid Supply Chain records to publish."
            )

            return 0

        producer = self.kafka_client.create_producer()

        published_count = 0

        try:

            for record in valid_records:

                key = str(
                    record["order_id"]
                )

                future = producer.send(
                    settings.kafka_supply_topic,
                    key=key,
                    value=record,
                )

                future.get(
                    timeout=10
                )

                published_count += 1

            producer.flush()

        finally:

            producer.close()

        logger.success(
            "Supply Chain API ingestion completed. "
            f"Published {published_count} records to "
            f"'{settings.kafka_supply_topic}'."
        )

        return published_count
# docker exec -it retailflow-airflow-scheduler-1 bash
# >> cd /opt/airflow/project
# python -m scripts.run_mock_supply_api
# python -m scripts.run_supply_chain_api
# python -m scripts.run_supply_orders_bronze