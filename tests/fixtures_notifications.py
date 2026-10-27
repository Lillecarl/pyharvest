from __future__ import annotations

from typing import Any

# Synthetic records shaped like live responses. Any: raw JSON bodies.


def notification(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 900,
        "notification_type": "timesheet_submitted",
        "category": "timesheets",
        "occurred_at": "2024-03-01T16:04:12Z",
        "read_at": None,
        "updated_at": "2024-03-01T16:04:12Z",
        "title": "Ada Lovelace submitted a timesheet for approval",
        "summary": "Week of February 26, 2024",
        **overrides,
    }


def unread_count(**overrides: Any) -> dict[str, Any]:
    return {"total": 3, "by_category": {"timesheets": 2, "timeoff": 1}, **overrides}


def notification_settings(**overrides: Any) -> dict[str, Any]:
    return {
        "channels": [
            {
                "notification_type": "timesheet_submitted_person",
                "channel": "in_app",
                "enabled": True,
                "feed_type": "timesheet_submitted",
                "category": "timesheets",
            },
            {
                "notification_type": "occasional_updates",
                "channel": "email",
                "enabled": True,
                "feed_type": None,
                "category": None,
            },
        ],
        "weekly_report": {"enabled": True},
        "approval_confirmation": {"enabled": False},
        "reminders": {
            "enabled": True,
            "time_of_day": 59400,
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            "via_desktop": True,
            "via_slack": False,
            "team_wide": False,
        },
        **overrides,
    }
