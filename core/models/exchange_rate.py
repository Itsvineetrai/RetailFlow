from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass(slots=True)
class ExchangeRate:
    """
    Exchange rate for converting a foreign currency
    into the base currency (USD).
    """

    currency: str
    rate_to_usd: Decimal
    effective_timestamp: datetime