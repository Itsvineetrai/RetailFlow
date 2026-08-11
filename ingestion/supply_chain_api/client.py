"""
RetailFlow Supply Chain REST API Client.

Responsible only for communicating with the external
Supply Chain REST API.

Responsibilities:
    - HTTP requests
    - timeout handling
    - retry handling
    - response validation at transport level
    - structured logging

Business validation belongs to validator.py.
Kafka publishing belongs to pipeline.py.
"""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from core.config import settings
from core.exceptions import APIError
from core.logger import get_logger

logger = get_logger(__name__)


class SupplyChainAPIClient:
    """
    Client for the external Supply Chain REST API.
    """

    def __init__(self) -> None:
        self.base_url = settings.supply_api_base_url.rstrip("/")
        self.endpoint = settings.supply_api_endpoint

        self.timeout = httpx.Timeout(
            settings.supply_api_timeout_seconds
        )

        if not self.base_url:
            raise APIError(
                "SUPPLY_API_BASE_URL is not configured."
            )

    @property
    def url(self) -> str:
        """
        Build the complete API URL.
        """
        return f"{self.base_url}/{self.endpoint.lstrip('/')}"

    @retry(
        stop=stop_after_attempt(
            settings.supply_api_max_retries
        ),
        wait=wait_exponential(
            multiplier=1,
            min=1,
            max=8,
        ),
        retry=retry_if_exception_type(
            (
                httpx.ConnectError,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError,
            )
        ),
        reraise=True,
    )
    def fetch_orders(self) -> list[dict[str, Any]]:
        """
        Fetch supply-chain orders from the REST API.

        Returns
        -------
        list[dict[str, Any]]
            API records.

        Raises
        ------
        APIError
            If the API request fails or returns an invalid response.
        """

        logger.info(
            f"Fetching Supply Chain API: {self.url}"
        )

        try:
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:

                response = client.get(self.url)

                response.raise_for_status()

                payload = response.json()

        except httpx.HTTPStatusError as exc:

            logger.error(
                "Supply Chain API returned HTTP error: "
                f"{exc.response.status_code}"
            )

            raise APIError(
                f"Supply Chain API HTTP error: "
                f"{exc.response.status_code}"
            ) from exc

        except (
            httpx.ConnectError,
            httpx.ReadTimeout,
            httpx.RemoteProtocolError,
        ):

            logger.warning(
                "Temporary Supply Chain API connection failure. "
                "Retrying..."
            )

            raise

        except ValueError as exc:

            logger.error(
                "Supply Chain API returned invalid JSON."
            )

            raise APIError(
                "Supply Chain API returned invalid JSON."
            ) from exc

        except httpx.HTTPError as exc:

            logger.error(
                f"Supply Chain API request failed: {exc}"
            )

            raise APIError(
                f"Supply Chain API request failed: {exc}"
            ) from exc

        if isinstance(payload, list):

            records = payload

        elif isinstance(payload, dict):

            records = payload.get("data")

            if records is None:
                records = payload.get("orders")

        else:

            raise APIError(
                "Unexpected Supply Chain API response format."
            )

        if not isinstance(records, list):

            raise APIError(
                "Supply Chain API response does not contain "
                "a list of records."
            )

        logger.success(
            f"Fetched {len(records)} supply-chain records."
        )

        return records