from __future__ import annotations

from typing import Any


def teammate(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 7,
        "first_name": "Charles",
        "last_name": "Babbage",
        "email": "charles@example.com",
        **overrides,
    }


def rate(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 20,
        "amount": 8.25,
        "start_date": "2024-01-01",
        "end_date": None,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def project_assignment(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 30,
        "is_project_manager": False,
        "is_active": True,
        "use_default_rates": True,
        "budget": None,
        "hourly_rate": None,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        "project": {"id": 3, "name": "Engine", "code": None, "is_billable": True},
        "client": {"id": 2, "name": "ABC Corp", "currency": "EUR"},
        "task_assignments": [
            {
                "id": 31,
                "billable": True,
                "is_active": True,
                "hourly_rate": None,
                "budget": 12.5,
                "created_at": "2024-01-02T03:04:05Z",
                "updated_at": "2024-01-02T03:04:05Z",
                "task": {"id": 4, "name": "Programming"},
            }
        ],
        **overrides,
    }
