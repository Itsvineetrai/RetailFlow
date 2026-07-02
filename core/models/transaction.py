from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(slots=True)
class Transaction:
    """
    Canonical transaction model shared across
    Generator, Kafka, Spark and Reconciliation.
    """

    transaction_id: str
    transaction_timestamp: datetime
    customer_id: str
    product_id: str
    store_id: str
    country: str
    currency: str
    amount: Decimal
    quantity: int
    payment_method: str
    sales_channel: str
    discount: Decimal
    tax: Decimal
    total_amount: Decimal
    is_return: bool
    ingestion_timestamp: Optional[datetime] = None