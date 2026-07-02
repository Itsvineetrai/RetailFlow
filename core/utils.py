"""
Common utility functions used throughout the AeroMart Data Platform.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4


def generate_uuid() -> str:
    """
    Generate a unique identifier.
    """
    return str(uuid4())


def current_timestamp() -> str:
    """
    Return current UTC timestamp.
    """
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


def round_currency(value: Decimal) -> Decimal:
    """
    Round financial values using bank-safe precision.
    """
    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def safe_decimal(value: str | float | int) -> Decimal:
    """
    Safely convert a value into Decimal.
    """
    return Decimal(str(value))


def utc_now() -> datetime:
    """
    Return timezone-aware UTC datetime.
    """
    return datetime.now(UTC)