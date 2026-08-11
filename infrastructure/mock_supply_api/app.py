"""
RetailFlow Mock Supply Chain REST API.

This service exists only for local development and integration testing.

It simulates an external Supply Chain API that provides order data.

Production deployments should replace this service with the actual
external Supply Chain API by changing SUPPLY_API_BASE_URL.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI

from core.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="RetailFlow Mock Supply Chain API",
    version="1.0.0",
)


def _orders() -> list[dict[str, Any]]:
    """
    Generate deterministic development supply-chain orders.

    Returns
    -------
    list[dict[str, Any]]
        Mock supply-chain orders.
    """

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    return [
        {
            "order_id": "PO-10001",
            "supplier_id": "SUP001",
            "product_id": "PRD0001",
            "quantity": 500,
            "status": "CREATED",
            "order_timestamp": timestamp,
            "expected_delivery_date": "2026-08-15",
            "warehouse_id": "WH001",
            "country": "India",
        },
        {
            "order_id": "PO-10002",
            "supplier_id": "SUP002",
            "product_id": "PRD0002",
            "quantity": 250,
            "status": "IN_TRANSIT",
            "order_timestamp": timestamp,
            "expected_delivery_date": "2026-08-13",
            "warehouse_id": "WH002",
            "country": "India",
        },
        {
            "order_id": "PO-10003",
            "supplier_id": "SUP003",
            "product_id": "PRD0005",
            "quantity": 1000,
            "status": "CREATED",
            "order_timestamp": timestamp,
            "expected_delivery_date": "2026-08-18",
            "warehouse_id": "WH001",
            "country": "India",
        },
    ]


@app.get("/health")
def health() -> dict[str, str]:
    """
    Health endpoint.
    """

    return {
        "status": "healthy",
        "service": "mock-supply-chain-api",
    }


@app.get("/orders")
def get_orders() -> dict[str, Any]:
    """
    Return mock supply-chain orders.
    """

    orders = _orders()

    logger.info(
        f"Mock Supply Chain API returning {len(orders)} orders."
    )

    return {
        "data": orders,
        "count": len(orders),
    }