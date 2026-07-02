"""
Serialize Transaction objects before publishing to Kafka.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
import json

from core.models.transaction import Transaction


class TransactionEncoder(json.JSONEncoder):
    """
    JSON encoder supporting Decimal and datetime.
    """

    def default(self, obj):

        if isinstance(obj, Decimal):
            return str(obj)

        if isinstance(obj, datetime):
            return obj.isoformat()

        return super().default(obj)


def serialize(transaction: Transaction) -> bytes:
    """
    Convert Transaction object to JSON bytes.
    """

    payload = asdict(transaction)

    return json.dumps(
        payload,
        cls=TransactionEncoder,
    ).encode("utf-8")