from __future__ import annotations

from typing import Any

# Synthetic report records shaped like live responses. Any: these are raw
# JSON bodies handed to respx, the shape the models parse.


def time_by_project(**overrides: Any) -> dict[str, Any]:
    return {
        "project_id": 3,
        "project_name": "Engine",
        "client_id": 2,
        "client_name": "ABC Corp",
        "total_hours": 4.5,
        "billable_hours": 3.5,
        "currency": None,
        "billable_amount": None,
        **overrides,
    }


def detailed_time_row(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 100,
        "spent_date": "2024-03-01",
        "hours": 2.25,
        "billable": True,
        "is_billed": False,
        "approval_status": "approved",
        "notes": "Analytical engine",
        "client_id": 2,
        "client_name": "ABC Corp",
        "project_id": 3,
        "project_name": "[ENG] Engine",
        "task_id": 4,
        "task_name": "Programming",
        "user_id": 1,
        "user_name": "Ada Lovelace",
        **overrides,
    }


def project_budget(**overrides: Any) -> dict[str, Any]:
    return {
        "project_id": 3,
        "project_name": "Engine",
        "client_id": 2,
        "client_name": "ABC Corp",
        "budget_is_monthly": False,
        "budget_by": "project",
        "is_active": True,
        "budget": 200,
        "budget_spent": 4,
        "budget_remaining": 196,
        **overrides,
    }


def saved_report(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 7,
        "name": "Billable time by client",
        "description": None,
        "configuration": {
            "subject": "time",
            "view": "summary",
            "levels": [{"kind": "column", "id": "client"}],
            "columns": ["hours"],
            "sort": None,
            "include_zero_values": False,
        },
        "lock_version": 3,
        "owner": {"id": 1, "name": "Ada Lovelace"},
        "is_owner": True,
        "can_edit": True,
        "created_at": "2024-03-01T10:00:00Z",
        "updated_at": "2024-03-01T12:00:00Z",
        **overrides,
    }


def generated_report(**overrides: Any) -> dict[str, Any]:
    return {
        "generated_report": {
            "report_id": None,
            "subject": "time",
            "columns": [
                {"id": "client", "label": "Client", "type": "text"},
                {"id": "hours", "label": "Hours", "type": "number"},
            ],
            "rows": [{"row": 0, "client": "ABC Corp", "hours": 12.5}],
            "row_count": 1,
            "overflow": False,
            "warnings": [],
            **overrides,
        }
    }


def report_export(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 42,
        "type": "detailed_time_report",
        "format": "csv",
        "status": "pending",
        "created_at": "2024-03-01T10:00:00Z",
        "completed_at": None,
        "download_url": None,
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
