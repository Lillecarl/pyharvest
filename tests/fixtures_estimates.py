from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses. Any: these are raw
# JSON bodies handed to respx, the shape the models parse.


def estimate(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 200,
        "client_key": "0123456789abcdef",
        "number": "1001",
        "purchase_order": None,
        "amount": 5250.0,
        "tax": 5.0,
        "tax_amount": 250.0,
        "tax2": None,
        "tax2_amount": 0.0,
        "discount": None,
        "discount_amount": 0.0,
        "subject": "Engine, phase 1",
        "notes": None,
        "state": "draft",
        "issue_date": None,
        "sent_at": None,
        "accepted_at": None,
        "declined_at": None,
        "currency": "EUR",
        "client": {"id": 2, "name": "ABC Corp"},
        "creator": {"id": 1, "name": "Ada Lovelace"},
        "line_items": [
            {
                "id": 201,
                "kind": "Service",
                "description": "Difference engine",
                "quantity": 1.0,
                "unit_price": 5000.0,
                "amount": 5000.0,
                "taxed": True,
                "taxed2": False,
            }
        ],
        "created_at": "2024-03-01T10:00:00Z",
        "updated_at": "2024-03-01T12:00:00Z",
        **overrides,
    }


def estimate_message(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 300,
        "sent_by": "Ada Lovelace",
        "sent_by_email": "ada@example.com",
        "sent_from": "Ada Lovelace",
        "sent_from_email": "ada@example.com",
        "send_me_a_copy": False,
        "recipients": [],
        "event_type": "send",
        "subject": None,
        "body": None,
        "created_at": "2024-03-01T10:00:00Z",
        "updated_at": "2024-03-01T10:00:00Z",
        **overrides,
    }


def estimate_item_category(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 400,
        "name": "Service",
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }
