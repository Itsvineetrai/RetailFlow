from decimal import Decimal
from pathlib import Path

import pandas as pd


RATE_FILE = Path("metadata/exchange_rates.csv")


def load_exchange_rates() -> dict[str, Decimal]:
    """
    Load exchange rates from the metadata CSV.

    Returns:
        {
            "USD": Decimal("1.0000"),
            "EUR": Decimal("1.1700"),
            "INR": Decimal("0.0120")
        }
    """

    dataframe = pd.read_csv(RATE_FILE)

    rates = {}

    for row in dataframe.itertuples(index=False):
        rates[row.currency] = Decimal(str(row.rate_to_usd))

    return rates