"""
RetailFlow Payment Methods Master Data

Master payment methods used throughout the RetailFlow platform.

Used by:
- POS Batch Generator
- E-commerce Generator
- Financial Reporting
- Payment Analytics
- Reconciliation Pipeline
"""

from __future__ import annotations

PAYMENT_METHODS = [
    {
        "payment_method_id": "PM001",
        "payment_method": "Cash",
        "payment_type": "Offline",
        "provider": "Store",
        "requires_authorization": False,
        "supports_refund": True,
        "currency": "ALL",
    },
    {
        "payment_method_id": "PM002",
        "payment_method": "Credit Card",
        "payment_type": "Card",
        "provider": "Visa",
        "requires_authorization": True,
        "supports_refund": True,
        "currency": "ALL",
    },
    {
        "payment_method_id": "PM003",
        "payment_method": "Debit Card",
        "payment_type": "Card",
        "provider": "Mastercard",
        "requires_authorization": True,
        "supports_refund": True,
        "currency": "ALL",
    },
    {
        "payment_method_id": "PM004",
        "payment_method": "UPI",
        "payment_type": "Digital",
        "provider": "NPCI",
        "requires_authorization": True,
        "supports_refund": True,
        "currency": "INR",
    },
    {
        "payment_method_id": "PM005",
        "payment_method": "Wallet",
        "payment_type": "Digital",
        "provider": "Paytm",
        "requires_authorization": True,
        "supports_refund": True,
        "currency": "INR",
    },
    {
        "payment_method_id": "PM006",
        "payment_method": "Bank Transfer",
        "payment_type": "Bank",
        "provider": "SWIFT",
        "requires_authorization": True,
        "supports_refund": False,
        "currency": "ALL",
    },
]