"""
RetailFlow Tax Reference Data

Country-wise tax reference table.

Used by:
- POS Generator
- Financial Engine
- Reconciliation
- Gold Layer
"""

from __future__ import annotations

TAX_RATES = {
    "IN": {
        "GST_5": 5,
        "GST_12": 12,
        "GST_18": 18,
        "GST_28": 28,
    },
    "US": {
        "STANDARD": 8,
    },
    "CA": {
        "HST": 13,
    },
    "GB": {
        "VAT": 20,
    },
    "DE": {
        "VAT": 19,
    },
}