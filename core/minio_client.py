"""
RetailFlow MinIO Client

Centralized MinIO client.

Every ingestion pipeline should use this client.

Usage:

from core.minio_client import MinIOClient

client = MinIOClient()

client.create_bucket("landing")
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

            self.client = Minio(
                endpoint=settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=False,
            )

            logger.success("Connected to MinIO.")

        except Exception as exc:

            logger.exception("Unable to connect to MinIO.")

            raise MinIOConnectionError(str(exc))

    def bucket_exists(
        self,
        bucket_name: str,
    ) -> bool:

        return self.client.bucket_exists(bucket_name)

    def create_bucket(
        self,
        bucket_name: str,
    ) -> None:

        try:

            if not self.client.bucket_exists(bucket_name):

                self.client.make_bucket(bucket_name)

                logger.success(
                    f"Bucket '{bucket_name}' created."
                )

            else:

                logger.info(
                    f"Bucket '{bucket_name}' already exists."
                )

        except S3Error as exc:

            logger.exception(exc)

            raise BucketNotFoundError(str(exc))

    def list_buckets(self):

        return self.client.list_buckets()

    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_path: str,
    ) -> None:

        self.client.fput_object(
            bucket_name,
            object_name,
            file_path,
        )

        logger.info(
            f"Uploaded {object_name}"
        )

    def download_file(
        self,
        bucket_name: str,
        object_name: str,
        file_path: str,
    ) -> None:

        self.client.fget_object(
            bucket_name,
            object_name,
            file_path,
        )

        logger.info(
            f"Downloaded {object_name}"
        )

    def delete_object(
        self,
        bucket_name: str,
        object_name: str,
    ) -> None:

        self.client.remove_object(
            bucket_name,
            object_name,
        )

        logger.info(
            f"Deleted {object_name}"
        )