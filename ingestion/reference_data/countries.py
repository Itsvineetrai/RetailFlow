"""
RetailFlow Country Reference Data

Reference data for supported countries.

Used by:
- POS Batch Generator
- Supply Chain
- Currency Conversion
- Financial Reporting
"""

from __future__ import annotations

COUNTRIES = [
    {
        "country_code": "IN",
        "country_name": "India",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "default_tax_rate": 18,
    },
    {
        "country_code": "US",
        "country_name": "United States",
        "currency": "USD",
        "timezone": "America/New_York",
        "default_tax_rate": 8,
    },
    {
        "country_code": "CA",
        "country_name": "Canada",
        "currency": "CAD",
        "timezone": "America/Toronto",
        "default_tax_rate": 13,
    },
    {
        "country_code": "GB",
        "country_name": "United Kingdom",
        "currency": "GBP",
        "timezone": "Europe/London",
        "default_tax_rate": 20,
    },
    {
        "country_code": "DE",
        "country_name": "Germany",
        "currency": "EUR",
        "timezone": "Europe/Berlin",
        "default_tax_rate": 19,
    },
]