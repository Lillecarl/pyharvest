from __future__ import annotations

from typing import Any

# Synthetic records shaped like live responses. Any: these are raw JSON
# bodies handed to respx, the shape the models parse.


def expense(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 500,
        "spent_date": "2024-03-01",
        "notes": "Train to Manchester",
        "total_cost": 33.35,
        "units": 1.0,
        "billable": True,
        "receipt": {
            "url": "https://example.com/expenses/500/receipt",
            "file_name": "ticket.pdf",
            "file_size": 39410,
            "content_type": "application/pdf",
        },
        "approval_status": "unsubmitted",
        "is_closed": False,
        "is_locked": False,
        "is_explicitly_locked": False,
        "is_billed": False,
        "locked_reason": None,
        "reimbursement": False,
        "created_at": "2024-03-01T10:00:00Z",
        "updated_at": "2024-03-01T12:00:00Z",
        "user": {"id": 1, "name": "Ada Lovelace"},
        "client": {"id": 2, "name": "ABC Corp", "currency": "EUR"},
        "project": {"id": 3, "name": "Engine", "code": None},
        "expense_category": {
            "id": 7,
            "name": "Travel",
            "unit_name": None,
            "unit_price": None,
        },
        "user_assignment": {
            "id": 5,
            "is_project_manager": False,
            "is_active": True,
            "use_default_rates": True,
            "budget": None,
            "hourly_rate": None,
            "created_at": "2024-01-02T03:04:05Z",
            "updated_at": "2024-01-02T03:04:05Z",
        },
        "invoice": None,
        **overrides,
    }


def expense_category(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 7,
        "name": "Mileage",
        "unit_name": "mile",
        "unit_price": 0.535,
        "is_active": True,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }
