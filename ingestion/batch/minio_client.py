"""
MinIO Client Wrapper.
"""

from minio import Minio
from core.config import get_config

config = get_config()


class MinIOClient:

    def __init__(self):

        self.client = Minio(
            endpoint="minio:9000",
            access_key=config.get(
                "minio",
                "access_key",
            ),
            secret_key=config.get(
                "minio",
                "secret_key",
            ),
            secure=False,
        )

    def upload_file(
        self,
        bucket: str,
        object_name: str,
        file_path: str,
    ) -> None:
        """
        Upload a file to MinIO.
        """

        self.client.fput_object(
            bucket_name=bucket,
            object_name=object_name,
            file_path=file_path,
        )

    def bucket_exists(self, bucket: str) -> bool:
        """
        Check whether a bucket exists.
        """

        return self.client.bucket_exists(bucket)