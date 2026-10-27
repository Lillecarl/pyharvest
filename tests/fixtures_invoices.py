from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses. The test account
# cannot read invoices (403), so the docs are the only source.


def invoice_line_item(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 700,
        "kind": "Service",
        "description": "Difference engine design",
        "quantity": 2.0,
        "unit_price": 150.0,
        "amount": 300.0,
        "taxed": True,
        "taxed2": False,
        "project": {"id": 3, "name": "Engine", "code": "ENG"},
        **overrides,
    }


def invoice(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 500,
        "client_key": "0123456789abcdef0123456789abcdef01234567",
        "number": "2024-001",
        "purchase_order": "",
        "amount": 330.0,
        "due_amount": 330.0,
        "tax": 10.0,
        "tax_amount": 30.0,
        "tax2": None,
        "tax2_amount": 0.0,
        "discount": None,
        "discount_amount": 0.0,
        "subject": "Engine, phase 1",
        "notes": None,
        "state": "open",
        "period_start": "2024-03-01",
        "period_end": "2024-03-31",
        "issue_date": "2024-04-01",
        "due_date": "2024-04-15",
        "payment_term": "net 15",
        "sent_at": "2024-04-01T09:00:00Z",
        "paid_at": None,
        "paid_date": None,
        "closed_at": None,
        "recurring_invoice_id": None,
        "created_at": "2024-04-01T08:00:00Z",
        "updated_at": "2024-04-01T09:00:00Z",
        "currency": "EUR",
        "payment_options": ["credit_card"],
        "client": {"id": 2, "name": "ABC Corp"},
        "estimate": None,
        "retainer": None,
        "creator": {"id": 1, "name": "Ada Lovelace"},
        "line_items": [invoice_line_item()],
        **overrides,
    }


def invoice_message(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 800,
        "sent_by": "Ada Lovelace",
        "sent_by_email": "ada@example.com",
        "sent_from": "Ada Lovelace",
        "sent_from_email": "ada@example.com",
        "include_link_to_client_invoice": False,
        "send_me_a_copy": False,
        "thank_you": False,
        "reminder": False,
        "send_reminder_on": None,
        "created_at": "2024-04-01T09:00:00Z",
        "updated_at": "2024-04-01T09:00:00Z",
        "attach_pdf": False,
        "event_type": None,
        "recipients": [{"name": "Charles Babbage", "email": "charles@example.com"}],
        "subject": "Invoice 2024-001",
        "body": "Please find the invoice attached.",
        **overrides,
    }


def invoice_payment(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 900,
        "amount": 330.0,
        "paid_at": "2024-04-10T12:00:00Z",
        "paid_date": "2024-04-10",
        "recorded_by": "Ada Lovelace",
        "recorded_by_email": "ada@example.com",
        "notes": "Bank transfer",
        "transaction_id": None,
        "created_at": "2024-04-10T12:05:00Z",
        "updated_at": "2024-04-10T12:05:00Z",
        "payment_gateway": {"id": None, "name": None},
        **overrides,
    }


def invoice_item_category(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 600,
        "name": "Service",
        "use_as_service": True,
        "use_as_expense": False,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }
