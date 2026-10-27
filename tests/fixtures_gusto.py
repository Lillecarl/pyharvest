from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses. Any: raw JSON bodies.


def sync_run(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 4000,
        "status": "queued",
        "run_type": "time_sheet",
        "date_range_start": "2024-03-04",
        "date_range_end": "2024-03-10",
        "gusto_payroll_uuid": None,
        "workweek_anchor": "Sunday",
        "initiated_by_user_id": 1,
        "created_at": "2024-03-11T14:30:00Z",
        "started_at": None,
        "completed_at": None,
        "terminal_error_message": None,
        "created_count": 0,
        "skipped_count": 0,
        "error_count": 0,
        **overrides,
    }


def sync_preview(**overrides: Any) -> dict[str, Any]:
    return {
        "date_range_start": "2024-03-04",
        "date_range_end": "2024-03-10",
        "gusto_payroll_uuid": None,
        "locked_filtered_count": 0,
        "api_errors": [],
        "projects": [
            {
                "user_mapping_id": 50,
                "user_id": 1,
                "project_id": 3,
                "dominant_state": "syncable",
                "entry_count": 3,
                "total_hours": 12.5,
                "state_counts": {"syncable": 3, "already_synced": 0},
                "job_required": True,
                "suggested_job_uuid": "job-1",
                "available_jobs": [{"uuid": "job-1", "title": "Engineer"}],
            }
        ],
        **overrides,
    }


def user_mapping(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 50,
        "user_id": 1,
        "gusto_entity_type": "Employee",
        "gusto_entity_uuid": "person-1",
        **overrides,
    }


def settings(**overrides: Any) -> dict[str, Any]:
    return {
        "connected": True,
        "needs_reconnect": False,
        "gusto_company_name": "Analytical Engines Ltd",
        "workweek_anchor": "Sunday",
        "workweek_anchor_editable": True,
        "sync_reminder": {
            "enabled": True,
            "frequency": "weekly",
            "weekday": "Monday",
            "monthly_position": None,
            "semimonthly_position_one": None,
            "semimonthly_position_two": None,
        },
        "user_mappings": [user_mapping()],
        **overrides,
    }
