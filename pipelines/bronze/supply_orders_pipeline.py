from __future__ import annotations

from core.constants import (
    BRONZE_SUPPLY_ORDERS_PATH,
    SUPPLY_ORDERS_CHECKPOINT_PATH,
)

from core.logger import get_logger

from ingestion.supply_chain_api.streaming import (
    SupplyChainStreamingPipeline,
)

from pipelines.bronze.bronze_writer import BronzeWriter


logger = get_logger(__name__)


class SupplyOrdersBronzePipeline:
    """
    Supply Chain API → Kafka → Spark → Bronze Delta.

    Flow:

        Kafka: supply.orders
                ↓
        Spark Structured Streaming
                ↓
        BronzeWriter
                ↓
        bronze/supply_orders
    """

    def __init__(self) -> None:

        self.pipeline = SupplyChainStreamingPipeline()

        # Centralized Bronze Delta writer
        self.bronze_writer = BronzeWriter()

    def start(self):

        logger.info(
            "Starting Supply Chain → Bronze pipeline..."
        )

        # --------------------------------------------------------------
        # 1. Read Supply Chain Kafka stream
        # --------------------------------------------------------------

        stream_df = self.pipeline.read_stream()

        # --------------------------------------------------------------
        # 2. Write to Supply Orders Bronze Delta
        # --------------------------------------------------------------

        query = self.bronze_writer.write_stream(
            dataframe=stream_df,
            checkpoint_path=SUPPLY_ORDERS_CHECKPOINT_PATH,
            output_path=BRONZE_SUPPLY_ORDERS_PATH,
        )

        logger.success(
            "Supply Chain → Bronze streaming pipeline started."
        )

        # Keep streaming job alive
        query.awaitTermination()