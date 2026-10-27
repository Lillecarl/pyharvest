from __future__ import annotations

from typing import Any

# Synthetic records shaped like live responses. Any: these are raw JSON
# bodies handed to respx, the shape the models parse.


def user(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 1,
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "telephone": "",
        "timezone": "Europe/Stockholm",
        "weekly_capacity": 144000,
        "has_access_to_all_future_projects": False,
        "is_contractor": False,
        "is_active": True,
        "employee_id": None,
        "calendar_integration_enabled": False,
        "calendar_integration_source": None,
        "can_create_projects": False,
        "roles": [],
        "access_roles": ["member"],
        "permissions_profile": "member",
        "permissions_claims": ["expenses:read:own"],
        "avatar_url": "https://example.com/avatar.png",
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def time_entry(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 100,
        "spent_date": "2024-03-01",
        "user": {"id": 1, "name": "Ada Lovelace"},
        "client": {"id": 2, "name": "ABC Corp", "currency": "EUR"},
        "project": {"id": 3, "name": "Engine", "code": "ENG"},
        "task": {"id": 4, "name": "Programming"},
        "user_assignment": {
            "id": 5,
            "is_project_manager": False,
            "is_active": True,
            "use_default_rates": True,
            "budget": None,
            "created_at": "2024-01-02T03:04:05Z",
            "updated_at": "2024-01-02T03:04:05Z",
            "hourly_rate": 100.0,
        },
        "task_assignment": {
            "id": 6,
            "billable": True,
            "is_active": True,
            "created_at": "2024-01-02T03:04:05Z",
            "updated_at": "2024-01-02T03:04:05Z",
            "hourly_rate": 100.0,
            "budget": None,
        },
        "hours": 2.11,
        "hours_without_timer": 2.11,
        "rounded_hours": 2.25,
        "notes": "Analytical engine",
        "is_locked": False,
        "is_explicitly_locked": False,
        "locked_reason": None,
        "approval_status": "unsubmitted",
        "is_closed": False,
        "is_billed": False,
        "timer_started_at": None,
        "started_time": None,
        "ended_time": None,
        "is_running": False,
        "billable": True,
        "budgeted": True,
        "billable_rate": None,
        "cost_rate": None,
        "invoice": None,
        "external_reference": None,
        "created_at": "2024-03-01T10:00:00Z",
        "updated_at": "2024-03-01T12:00:00Z",
        **overrides,
    }


def page(
    key: str, records: list[dict[str, Any]], next_url: str | None
) -> dict[str, Any]:
    return {
        key: records,
        "per_page": 2000,
        "total_pages": None,
        "total_entries": None,
        "page": None,
        "next_page": None,
        "previous_page": None,
        "links": {"first": None, "next": next_url, "previous": None, "last": None},
    }
