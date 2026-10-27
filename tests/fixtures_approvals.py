from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses. Any: raw JSON bodies.


def approval(**overrides: Any) -> dict[str, Any]:
    return {
        "user_id": 1,
        "user_name": "Ada Lovelace",
        "avatar_url": None,
        "total_hours": 32.5,
        "billable_hours": 24.0,
        "has_running_timer": False,
        "expenses_by_currency": [
            {"currency": "EUR", "total_amount": 145.5, "billable_amount": 100.25}
        ],
        **overrides,
    }


def submission(**overrides: Any) -> dict[str, Any]:
    return {
        "user_id": 1,
        "period_start": "2024-03-04",
        "period_end": "2024-03-10",
        "status": "submitted",
        "timesheet_version": "0f1e2d3c4b5a69788796a5b4c3d2e1f0",
        **overrides,
    }
