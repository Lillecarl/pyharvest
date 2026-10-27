from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses. Any: raw JSON bodies.

PTO_TYPE = {"id": 20, "name": "Vacation", "color": "blue", "icon": "vacation"}
USER = {"id": 1, "name": "Ada Lovelace"}


def work_schedule(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 10,
        "name": "Four days",
        "is_default": False,
        "is_active": True,
        "weekly_hours": 32.0,
        "monday_hours": 8.0,
        "tuesday_hours": 8.0,
        "wednesday_hours": 8.0,
        "thursday_hours": 8.0,
        "friday_hours": 0.0,
        "saturday_hours": 0.0,
        "sunday_hours": 0.0,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def time_off_request(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 30,
        "status": "pending",
        "start_date": "2024-03-04",
        "end_date": "2024-03-05",
        "days": 1.5,
        "business_days_at_submission": 2.0,
        "start_time_minutes": None,
        "end_time_minutes": 780,
        "notes": "Long weekend",
        "review_reason": None,
        "reviewed_at": None,
        "created_at": "2024-02-01T12:00:00Z",
        "updated_at": "2024-02-01T12:00:00Z",
        "user": USER,
        "pto_type": PTO_TYPE,
        "reviewer": None,
        "request_days": [
            {
                "id": 31,
                "date": "2024-03-04",
                "hours": 8.0,
                "day_fraction": 1.0,
                "created_at": "2024-02-01T12:00:00Z",
                "updated_at": "2024-02-01T12:00:00Z",
            },
            {
                "id": 32,
                "date": "2024-03-05",
                "hours": 4.0,
                "day_fraction": 0.5,
                "created_at": "2024-02-01T12:00:00Z",
                "updated_at": "2024-02-01T12:00:00Z",
            },
        ],
        "coverage_warnings": [
            {
                "user": {"id": 2, "name": "Charles Babbage"},
                "projects": [{"id": 3, "name": "Engine"}],
                "dates": ["2024-03-04"],
            }
        ],
        **overrides,
    }


def time_off_policy(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 20,
        "name": "Vacation",
        "color": "blue",
        "icon": "vacation",
        "accrual_type": "fixed",
        "accrual_schedule": "monthly",
        "default_days_per_year": 25.0,
        "max_carryover_days": 5.0,
        "requires_approval": True,
        "visible_to_all": True,
        "is_active": True,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def balance_sheet(**overrides: Any) -> dict[str, Any]:
    return {
        "user": USER,
        "year": 2024,
        "as_of": "2024-03-01",
        "balances": [
            {
                "pto_type": PTO_TYPE,
                "is_requestable": True,
                "year": 2024,
                "as_of": "2024-03-01",
                "is_unlimited": False,
                "requires_approval": True,
                "effective_accrual_type": "fixed",
                "accrual_schedule": "monthly",
                "accrued_days": "25.0",
                "carryover_days": "2.0",
                "available_days": "27.0",
                "used_days": "10.0",
                "pending_days": "3.0",
                "remaining_days": "14.0",
                "used_hours": "80.0",
                "pending_hours": "24.0",
                "used_fraction": "0.3704",
                "pending_fraction": "0.1111",
            }
        ],
        **overrides,
    }


def holiday_calendar(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 40,
        "name": "Office closures",
        "entries_count": 1,
        "entries": [{"id": 41, "name": "New Year's Day", "date": "2024-01-01"}],
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def holiday_calendar_entry(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 41,
        "pto_holiday_calendar_id": 40,
        "name": "New Year's Day",
        "date": "2024-01-01",
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def assignment(**overrides: Any) -> dict[str, Any]:
    return {
        "user": USER,
        "holiday_calendar": {"id": 40, "name": "Office closures"},
        "work_schedule": None,
        "effective_work_schedule": {"name": "Standard", "weekly_hours": 40.0},
        **overrides,
    }


def allocation(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 50,
        "year": 2024,
        "accrual_type": None,
        "accrual_schedule": None,
        "accrual_first_payday": None,
        "accrual_leave_hours": None,
        "accrual_worked_hours": None,
        "accrual_max_hours_per_year": None,
        "days_per_year": 28.0,
        "carryover_days": 2.0,
        "requires_approval": False,
        "effective_days_per_year": 28.0,
        "effective_accrual_type": "fixed",
        "effective_accrual_schedule": "monthly",
        "effective_requires_approval": False,
        "user": USER,
        "pto_type": PTO_TYPE,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def allocation_reset(**overrides: Any) -> dict[str, Any]:
    return {
        "user": USER,
        "pto_type": PTO_TYPE,
        "year": 2024,
        "customized": False,
        "message": "Allocation reset to type defaults",
        **overrides,
    }
