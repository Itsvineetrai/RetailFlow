"""
RetailFlow MinIO Client
Centralized MinIO client. Every ingestion pipeline should use this client.

Usage:
    from core.minio_client import MinIOClient
    client = MinIOClient()
    client.create_bucket()  # Automatically creates 'retailflow'
"""

from __future__ import annotations
from minio import Minio
from minio.error import S3Error
from core.config import settings
from core.logger import get_logger
from core.exceptions import (
    BucketNotFoundError,
    MinIOConnectionError,
)

logger = get_logger(__name__)


class MinIOClient:

    def __init__(self) -> None:
        try:
            # Force clean the endpoint string
            raw_endpoint = str(settings.minio_endpoint)
            if "://" in raw_endpoint:
                raw_endpoint = raw_endpoint.split("://")[-1]
            clean_endpoint = raw_endpoint.strip().rstrip("/")

            # OVERRIDE: If Windows is stuck trying to find 'minio', swap it to localhost
            if "minio" in clean_endpoint.lower() and "localhost" not in clean_endpoint.lower():
                clean_endpoint = clean_endpoint.lower().replace("minio", "localhost")

            logger.info(f"Connecting to MinIO endpoint: {clean_endpoint}")
            self.client = Minio(
                endpoint=clean_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=False,
            )
            logger.success("Connected to MinIO object.")
        except Exception as exc:
            logger.exception("Unable to connect to MinIO.")
            raise MinIOConnectionError(str(exc))

    def bucket_exists(self) -> bool:
        return self.client.bucket_exists("retailflow")

    def create_bucket(self) -> None:
        try:
            if not self.client.bucket_exists("retailflow"):
                self.client.make_bucket("retailflow")
                logger.success("Bucket 'retailflow' created.")
            else:
                logger.info("Bucket 'retailflow' already exists.")
        except S3Error as exc:
            logger.exception(exc)
            raise BucketNotFoundError(str(exc))

    def list_buckets(self):
        return self.client.list_buckets()

    def upload_file(
        self,
        object_name: str,
        file_path: str,
    ) -> None:
        self.client.fput_object(
            "retailflow",
            object_name,
            file_path,
        )
        logger.info(f"Uploaded {object_name} to retailflow bucket")

    def download_file(
        self,
        object_name: str,
        file_path: str,
    ) -> None:
        self.client.fget_object(
            "retailflow",
            object_name,
            file_path,
        )
        logger.info(f"Downloaded {object_name} from retailflow bucket")

    def delete_object(
        self,
        object_name: str,
    ) -> None:
        self.client.remove_object(
            "retailflow",
            object_name,
        )
        logger.info(f"Deleted {object_name} from retailflow bucket")
