"""
RetailFlow Currency Master Data

Master currency catalog used across the RetailFlow platform.

Used by:
- POS Batch Generator
- Financial Engine
- Currency Conversion
- Financial Reporting
- Batch Reconciliation
"""

from __future__ import annotations

CURRENCIES = [
    {
        "currency_code": "INR",
        "currency_name": "Indian Rupee",
        "symbol": "₹",
        "decimal_places": 2,
        "smallest_unit": "Paise",
        "country": "India",
        "active": True,
    },
    {
        "currency_code": "USD",
        "currency_name": "US Dollar",
        "symbol": "$",
        "decimal_places": 2,
        "smallest_unit": "Cent",
        "country": "United States",
        "active": True,
    },
    {
        "currency_code": "EUR",
        "currency_name": "Euro",
        "symbol": "€",
        "decimal_places": 2,
        "smallest_unit": "Cent",
        "country": "European Union",
        "active": True,
    },
    {
        "currency_code": "GBP",
        "currency_name": "British Pound",
        "symbol": "£",
        "decimal_places": 2,
        "smallest_unit": "Penny",
        "country": "United Kingdom",
        "active": True,
    },
    {
        "currency_code": "CAD",
        "currency_name": "Canadian Dollar",
        "symbol": "C$",
        "decimal_places": 2,
        "smallest_unit": "Cent",
        "country": "Canada",
        "active": True,
    },
]