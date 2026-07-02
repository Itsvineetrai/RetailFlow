"""
Generate mock e-commerce transactions.

Produces realistic retail events for Kafka streaming.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime
from decimal import Decimal

from faker import Faker

from core.models.transaction import Transaction

fake = Faker()

COUNTRIES = [
    "USA",
    "India",
    "Germany",
]

CURRENCIES = {
    "USA": "USD",
    "India": "INR",
    "Germany": "EUR",
}

PAYMENT_METHODS = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Wallet",
]

CHANNELS = [
    "Web",
    "Mobile",
]


def generate_transaction() -> Transaction:
    """
    Generate a single retail transaction.
    """

    country = random.choice(COUNTRIES)

    currency = CURRENCIES[country]

    quantity = random.randint(1, 5)

    amount = Decimal(
        str(
            round(
                random.uniform(20, 500),
                2,
            )
        )
    )

    tax = amount * Decimal("0.18")

    discount = amount * Decimal("0.05")

    total = amount + tax - discount

    return Transaction(
        transaction_id=fake.uuid4(),
        transaction_timestamp=datetime.now(UTC),
        customer_id=f"CUST-{random.randint(100000,999999)}",
        product_id=f"PROD-{random.randint(1000,9999)}",
        store_id=f"ONLINE-{random.randint(1,20)}",
        country=country,
        currency=currency,
        amount=amount,
        quantity=quantity,
        payment_method=random.choice(PAYMENT_METHODS),
        sales_channel=random.choice(CHANNELS),
        discount=discount,
        tax=tax,
        total_amount=total,
        is_return=False,
    )