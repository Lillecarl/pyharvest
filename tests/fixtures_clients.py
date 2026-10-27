from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses: this account may
# not read clients or contacts, so no live shape backs them.


def client(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 2,
        "name": "ABC Corp",
        "is_active": True,
        "address": "456 Main St.\r\nAnytown, CT 06467",
        "statement_key": "0123456789abcdef0123456789abcdef",
        "currency": "EUR",
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def contact(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 7,
        "client": {"id": 2, "name": "ABC Corp"},
        "title": "Owner",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone_office": "555-0100",
        "phone_mobile": "555-0101",
        "fax": "",
        "invoice_recipient_status": "none",
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }
