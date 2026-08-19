import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


MINIO_ENDPOINT = os.getenv(
    "MINIO_ENDPOINT",
    "http://localhost:9000",
)

if MINIO_ENDPOINT == "minio:9000":
    MINIO_ENDPOINT = "http://localhost:9000"

if not MINIO_ENDPOINT.startswith(("http://", "https://")):
    MINIO_ENDPOINT = f"http://{MINIO_ENDPOINT}"

MINIO_ACCESS_KEY = os.getenv(
    "MINIO_ROOT_USER"
)

MINIO_SECRET_KEY = os.getenv(
    "MINIO_ROOT_PASSWORD"
)


def get_storage_options() -> dict:
    if not MINIO_ACCESS_KEY:
        raise RuntimeError(
            "MINIO_ROOT_USER is missing from .env"
        )

    if not MINIO_SECRET_KEY:
        raise RuntimeError(
            "MINIO_ROOT_PASSWORD is missing from .env"
        )

    return {
        "AWS_ACCESS_KEY_ID": MINIO_ACCESS_KEY,
        "AWS_SECRET_ACCESS_KEY": MINIO_SECRET_KEY,
        "AWS_ENDPOINT_URL": MINIO_ENDPOINT,
        "AWS_REGION": "us-east-1",
        "AWS_ALLOW_HTTP": "true",
    }