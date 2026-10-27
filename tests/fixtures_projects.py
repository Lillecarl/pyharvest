from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses. Any: raw JSON
# bodies handed to respx.


def project(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 3,
        "name": "Engine",
        "code": "ENG",
        "is_active": True,
        "bill_by": "Project",
        "budget": 200.0,
        "budget_by": "project",
        "budget_is_monthly": False,
        "notify_when_over_budget": True,
        "over_budget_notification_percentage": 80.0,
        "over_budget_notification_date": None,
        "show_budget_to_all": False,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        "starts_on": "2024-01-01",
        "ends_on": None,
        "is_billable": True,
        "is_fixed_fee": False,
        "currency": "EUR",
        "notes": "",
        "client": {"id": 2, "name": "ABC Corp", "currency": "EUR"},
        "cost_budget": None,
        "cost_budget_include_expenses": False,
        "hourly_rate": 100.0,
        "fee": None,
        "tags": [{"id": 7, "name": "Design"}],
        **overrides,
    }


def user_assignment(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 5,
        "is_project_manager": False,
        "is_active": True,
        "use_default_rates": False,
        "budget": None,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        "hourly_rate": 75.5,
        "project": {"id": 3, "name": "Engine", "code": "ENG"},
        "user": {"id": 1, "name": "Ada Lovelace"},
        **overrides,
    }


def task_assignment(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 6,
        "billable": True,
        "is_active": True,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        "hourly_rate": 75.5,
        "budget": None,
        "project": {"id": 3, "name": "Engine", "code": None},
        "task": {"id": 4, "name": "Programming"},
        **overrides,
    }


def tag(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 7,
        "name": "Design",
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }
