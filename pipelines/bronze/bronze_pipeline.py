from __future__ import annotations

from core.constants import (
    APPEND,
    BRONZE_CHECKPOINT_PATH,
    BRONZE_TRANSACTIONS_PATH,
)

from core.logger import get_logger

from ingestion.ecommerce_stream.pipeline import (
    EcommerceStreamingPipeline,
)

logger = get_logger(__name__)


class BronzePipeline:

    def __init__(self):

        self.pipeline = EcommerceStreamingPipeline()

    def start(self):

        logger.info("Starting Bronze Delta Pipeline...")

        stream_df = self.pipeline.read_stream()

        query = (

            stream_df.writeStream

            .format("delta")

            .outputMode(APPEND)

            .option(
                "checkpointLocation",
                BRONZE_CHECKPOINT_PATH,
            )

            .option(
                "path",
                BRONZE_TRANSACTIONS_PATH,
            )

            .trigger(processingTime="10 seconds")

            .start()

        )

        logger.success(
            "Bronze Delta Streaming Started."
        )

        query.awaitTermination()


def main():

    BronzePipeline().start()


if __name__ == "__main__":

    main()