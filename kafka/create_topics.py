"""
Create Kafka topics required by the AeroMart platform.
"""

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from core.config import get_config
from core.logger import get_logger

logger = get_logger(__name__)
config = get_config()


def create_topics() -> None:

    admin = KafkaAdminClient(
        bootstrap_servers=config.get(
            "kafka",
            "bootstrap_servers",
        )
    )

    topics = [

        NewTopic(
            name=config.get(
                "kafka",
                "topics",
                "online_sales",
            ),
            num_partitions=12,
            replication_factor=1,
        ),

        NewTopic(
            name=config.get(
                "kafka",
                "topics",
                "dead_letter_queue",
            ),
            num_partitions=3,
            replication_factor=1,
        ),

    ]

    try:

        admin.create_topics(topics)

        logger.info("Kafka topics created.")

    except TopicAlreadyExistsError:

        logger.info("Topics already exist.")

    finally:

        admin.close()


if __name__ == "__main__":
    create_topics()