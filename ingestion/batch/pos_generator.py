"""
Generate mock POS (Point of Sale) transactions.
"""

from __future__ import annotations

import random
from decimal import Decimal
from datetime import UTC, datetime

from faker import Faker

from core.models.transaction import Transaction

fake = Faker()

COUNTRIES = ["USA", "India", "Germany"]

CURRENCIES = {
    "USA": "USD",
    "India": "INR",
    "Germany": "EUR",
}

PAYMENT_METHODS = [
    "Cash",
    "Credit Card",
    "Debit Card",
]

def generate_pos_transaction() -> Transaction:

    country = random.choice(COUNTRIES)

    amount = Decimal(
        str(round(random.uniform(5, 300), 2))
    )

    tax = amount * Decimal("0.18")

    discount = amount * Decimal("0.03")

    total = amount + tax - discount

    return Transaction(

        transaction_id=fake.uuid4(),

        transaction_timestamp=datetime.now(UTC),

        customer_id=f"CUST-{random.randint(100000,999999)}",

        product_id=f"PROD-{random.randint(1000,9999)}",

        store_id=f"STORE-{random.randint(1,100)}",

        country=country,

        currency=CURRENCIES[country],

        amount=amount,

        quantity=random.randint(1,5),

        payment_method=random.choice(PAYMENT_METHODS),

        sales_channel="POS",

        discount=discount,

        tax=tax,

        total_amount=total,

        is_return=False,
    )