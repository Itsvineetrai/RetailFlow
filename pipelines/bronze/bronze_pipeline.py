from __future__ import annotations

from core.constants import (
    BRONZE_CHECKPOINT_PATH,
    BRONZE_TRANSACTIONS_PATH,
)
from core.logger import get_logger

from ingestion.ecommerce_stream.pipeline import (
    EcommerceStreamingPipeline,
)
from pipelines.bronze.bronze_writer import BronzeWriter

logger = get_logger(__name__)


class BronzePipeline:
    """
    Streaming Bronze Pipeline.

    Flow:

        Kafka
          ↓
        Spark Structured Streaming
          ↓
        Bronze Delta
    """

    def __init__(self):

        self.pipeline = EcommerceStreamingPipeline()

        self.writer = BronzeWriter()

    def start(self):

        logger.info(
            "Starting Bronze Delta Pipeline..."
        )

        stream_df = self.pipeline.read_stream()

        query = self.writer.write_stream(
            dataframe=stream_df,
            checkpoint_path=BRONZE_CHECKPOINT_PATH,
            output_path=BRONZE_TRANSACTIONS_PATH,
            trigger_interval="10 seconds",
        )

        logger.success(
            "Bronze Delta Streaming Started."
        )

        query.awaitTermination()


def main():

    BronzePipeline().start()


if __name__ == "__main__":
    main()