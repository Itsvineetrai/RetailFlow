"""
Functions for injecting realistic bad data into the retail stream.

Used to test:
- DLQ
- Schema Validation
- Data Quality Rules
"""

from __future__ import annotations

import random
from decimal import Decimal


def inject_missing_customer(transaction: dict) -> dict:
    transaction["customer_id"] = None
    return transaction


def inject_negative_amount(transaction: dict) -> dict:
    transaction["amount"] = Decimal("-100.00")
    return transaction


def inject_invalid_currency(transaction: dict) -> dict:
    transaction["currency"] = "XYZ"
    return transaction


def inject_invalid_quantity(transaction: dict) -> dict:
    transaction["quantity"] = -5
    return transaction


def inject_empty_product(transaction: dict) -> dict:
    transaction["product_id"] = ""
    return transaction


ANOMALIES = [
    inject_missing_customer,
    inject_negative_amount,
    inject_invalid_currency,
    inject_invalid_quantity,
    inject_empty_product,
]


def apply_random_anomaly(
    transaction: dict,
    probability: float = 0.03,
) -> dict:
    """
    Inject an anomaly into a transaction.

    Default:
        3% bad records
    """

    if random.random() < probability:
        anomaly = random.choice(ANOMALIES)
        return anomaly(transaction)

    return transaction