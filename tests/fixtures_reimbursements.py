from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses. Any: raw JSON bodies.


def reimbursement(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 700,
        "status": "ready",
        "approval_status": "approved",
        "payout_ready": True,
        "payout_status": "ready",
        "reimbursement_status": None,
        "paid_on": None,
        "fee": None,
        "reference": None,
        "usd_amount": None,
        "rejected_reason": None,
        "spent_date": "2024-03-01",
        "total_cost": 33.35,
        "currency_code": "EUR",
        "notes": "Train ticket",
        "billable": True,
        "user": {"id": 1, "name": "Ada Lovelace"},
        "client": {"id": 2, "name": "ABC Corp"},
        "project": {"id": 3, "name": "Engine"},
        "expense_category": {"id": 8, "name": "Travel", "unit_name": None},
        **overrides,
    }
