"""
RetailFlow Exchange Rate Reference Data

Reference exchange rates used for development and testing.

NOTE:
In production these values would come from an external FX service.
"""

from __future__ import annotations

EXCHANGE_RATES = [
    {
        "base_currency": "USD",
        "target_currency": "INR",
        "exchange_rate": 86.25,
        "effective_from": "2026-01-01",
    },
    {
        "base_currency": "EUR",
        "target_currency": "INR",
        "exchange_rate": 100.15,
        "effective_from": "2026-01-01",
    },
    {
        "base_currency": "GBP",
        "target_currency": "INR",
        "exchange_rate": 116.40,
        "effective_from": "2026-01-01",
    },
    {
        "base_currency": "CAD",
        "target_currency": "INR",
        "exchange_rate": 63.80,
        "effective_from": "2026-01-01",
    },
    {
        "base_currency": "USD",
        "target_currency": "EUR",
        "exchange_rate": 0.91,
        "effective_from": "2026-01-01",
    },
]