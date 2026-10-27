from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import RootModel

from pyharvest.models.base import HarvestInput, HarvestModel, Open, Ref


class PtoAccrualType(StrEnum):
    FIXED = "fixed"
    ACCRUED = "accrued"
    UNLIMITED = "unlimited"


class PtoAccrualSchedule(StrEnum):
    MONTHLY = "monthly"
    BIWEEKLY = "biweekly"
    SEMIMONTHLY = "semimonthly"
    HOURLY = "hourly"


class TimeOffRequestStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    CHANGES_REQUESTED = "changes_requested"
    CANCELLED = "cancelled"


class PtoConflictResolution(StrEnum):
    SKIP = "skip"
    REPLACE = "replace"


class PtoTypeRef(Ref):
    """A time off policy stub."""

    color: str | None = None
    icon: str | None = None


# Work schedules


class WorkSchedule(HarvestModel):
    id: int
    name: str
    is_default: bool
    is_active: bool
    weekly_hours: Decimal
    monday_hours: Decimal
    tuesday_hours: Decimal
    wednesday_hours: Decimal
    thursday_hours: Decimal
    friday_hours: Decimal
    saturday_hours: Decimal
    sunday_hours: Decimal
    created_at: dt.datetime
    updated_at: dt.datetime


class WorkScheduleCreate(HarvestInput):
    name: str
    is_default: bool | None = None
    monday_hours: float | None = None
    tuesday_hours: float | None = None
    wednesday_hours: float | None = None
    thursday_hours: float | None = None
    friday_hours: float | None = None
    saturday_hours: float | None = None
    sunday_hours: float | None = None


class WorkScheduleUpdate(HarvestInput):
    name: str | None = None
    is_default: bool | None = None
    monday_hours: float | None = None
    tuesday_hours: float | None = None
    wednesday_hours: float | None = None
    thursday_hours: float | None = None
    friday_hours: float | None = None
    saturday_hours: float | None = None
    sunday_hours: float | None = None


# Time off requests


class TimeOffRequestDay(HarvestModel):
    id: int
    date: dt.date
    hours: Decimal
    day_fraction: Decimal
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None


class TimeOffCoverageWarning(HarvestModel):
    """A coworker who shares projects with the requester and is away too."""

    user: Ref
    projects: list[Ref]
    dates: list[dt.date]


class TimeOffRequest(HarvestModel):
    id: int
    status: Open[TimeOffRequestStatus]
    start_date: dt.date
    end_date: dt.date
    days: Decimal
    business_days_at_submission: Decimal | None = None
    # Minutes after midnight, for partial-day requests.
    start_time_minutes: int | None = None
    end_time_minutes: int | None = None
    notes: str | None = None
    review_reason: str | None = None
    reviewed_at: dt.datetime | None = None
    created_at: dt.datetime
    updated_at: dt.datetime
    user: Ref
    pto_type: PtoTypeRef
    reviewer: Ref | None = None
    request_days: list[TimeOffRequestDay]
    coverage_warnings: list[TimeOffCoverageWarning] | None = None
    """Only for administrators, on requests still awaiting a decision."""


class TimeOffRequestCreate(HarvestInput):
    pto_type_id: int
    start_date: dt.date
    end_date: dt.date
    user_id: int | None = None
    """Administrators only: book for another user."""
    notes: str | None = None
    start_time_minutes: int | None = None
    end_time_minutes: int | None = None
    conflict_resolution: PtoConflictResolution | None = None


class TimeOffRequestUpdate(HarvestInput):
    pto_type_id: int | None = None
    start_date: dt.date | None = None
    end_date: dt.date | None = None
    notes: str | None = None
    start_time_minutes: int | None = None
    end_time_minutes: int | None = None
    conflict_resolution: PtoConflictResolution | None = None


class TimeOffReview(HarvestInput):
    reason: str


class TimeOffBulkReview(HarvestInput):
    ids: list[int]
    reason: str | None = None


class TimeOffBulkResult(HarvestModel):
    pto_requests: list[TimeOffRequest]
    """The requests reviewed."""
    skipped_ids: list[int]
    """Requests not pending, left as they were."""


# Time off policies


class TimeOffPolicy(HarvestModel):
    id: int
    name: str
    color: str | None = None
    icon: str | None = None
    accrual_type: Open[PtoAccrualType]
    accrual_schedule: Open[PtoAccrualSchedule] | None = None
    accrual_first_payday: dt.date | None = None
    accrual_leave_hours: Decimal | None = None
    accrual_worked_hours: Decimal | None = None
    accrual_max_hours_per_year: Decimal | None = None
    default_days_per_year: Decimal | None = None
    max_carryover_days: Decimal | None = None
    requires_approval: bool
    visible_to_all: bool
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime


class TimeOffPolicyCreate(HarvestInput):
    name: str
    color: str | None = None
    icon: str | None = None
    accrual_type: PtoAccrualType | None = None
    accrual_schedule: PtoAccrualSchedule | None = None
    accrual_first_payday: dt.date | None = None
    accrual_leave_hours: float | None = None
    accrual_worked_hours: float | None = None
    accrual_max_hours_per_year: float | None = None
    default_days_per_year: float | None = None
    max_carryover_days: float | None = None
    requires_approval: bool | None = None
    visible_to_all: bool | None = None


class TimeOffPolicyUpdate(HarvestInput):
    name: str | None = None
    color: str | None = None
    icon: str | None = None
    accrual_type: PtoAccrualType | None = None
    accrual_schedule: PtoAccrualSchedule | None = None
    accrual_first_payday: dt.date | None = None
    accrual_leave_hours: float | None = None
    accrual_worked_hours: float | None = None
    accrual_max_hours_per_year: float | None = None
    default_days_per_year: float | None = None
    max_carryover_days: float | None = None
    requires_approval: bool | None = None
    visible_to_all: bool | None = None
    deactivated: bool | None = None
    """``False`` reactivates a deactivated policy."""


# Time off balances


class TimeOffBalance(HarvestModel):
    pto_type: PtoTypeRef
    is_requestable: bool
    year: int
    as_of: dt.date
    is_unlimited: bool
    requires_approval: bool
    effective_accrual_type: Open[PtoAccrualType] | None = None
    accrual_schedule: Open[PtoAccrualSchedule] | None = None
    accrued_days: Decimal | None = None
    carryover_days: Decimal | None = None
    available_days: Decimal | None = None
    used_days: Decimal
    pending_days: Decimal
    remaining_days: Decimal | None = None
    used_hours: Decimal
    pending_hours: Decimal
    used_fraction: Decimal | None = None
    pending_fraction: Decimal | None = None


class TimeOffBalanceSheet(HarvestModel):
    """One user's balances for a year, one entry per policy."""

    user: Ref
    year: int
    as_of: dt.date
    balances: list[TimeOffBalance]


# Holiday calendars


class HolidayCalendarDay(HarvestModel):
    """An entry as nested in a calendar."""

    id: int
    name: str
    date: dt.date


class HolidayCalendar(HarvestModel):
    id: int
    name: str
    entries_count: int
    entries: list[HolidayCalendarDay]
    created_at: dt.datetime
    updated_at: dt.datetime


class HolidayCalendarCreate(HarvestInput):
    name: str
    country_code: str | None = None
    """ISO country code, such as ``GB``: fills in national public holidays."""


class HolidayCalendarUpdate(HarvestInput):
    name: str
    """Harvest requires it; it is the only field."""


class HolidayCalendarEntry(HarvestModel):
    id: int
    pto_holiday_calendar_id: int
    name: str
    date: dt.date
    created_at: dt.datetime
    updated_at: dt.datetime


class HolidayCalendarEntryCreate(HarvestInput):
    """Pass ``date`` for one day, or ``date_mode="range"`` with
    ``start_date`` and ``end_date`` for several."""

    name: str
    date: dt.date | None = None
    date_mode: Literal["range"] | None = None
    start_date: dt.date | None = None
    end_date: dt.date | None = None


class HolidayCalendarEntryUpdate(HarvestInput):
    name: str | None = None
    date: dt.date | None = None


# User assignments


class PtoEffectiveWorkSchedule(HarvestModel):
    name: str
    weekly_hours: Decimal


class PtoAssignment(HarvestModel):
    """A user's holiday calendar and work schedule."""

    user: Ref
    holiday_calendar: Ref | None = None
    work_schedule: Ref | None = None
    """None when unassigned or deactivated."""
    effective_work_schedule: PtoEffectiveWorkSchedule | None = None


class PtoAssignmentUpdate(HarvestInput):
    """An explicit None unassigns; a work schedule then reverts to the
    company default."""

    holiday_calendar_id: int | None = None
    work_schedule_id: int | None = None


# Allocations


class PtoAllocation(HarvestModel):
    """A user's yearly allowance for one policy. The plain fields hold the
    user's overrides and are None where the policy default applies."""

    id: int | None = None
    """None in a bulk result for an item that holds no override."""
    year: int
    user: Ref
    pto_type: PtoTypeRef
    accrual_type: Open[PtoAccrualType] | None = None
    accrual_schedule: Open[PtoAccrualSchedule] | None = None
    accrual_first_payday: dt.date | None = None
    accrual_leave_hours: Decimal | None = None
    accrual_worked_hours: Decimal | None = None
    accrual_max_hours_per_year: Decimal | None = None
    days_per_year: Decimal | None = None
    carryover_days: Decimal | None = None
    deferred_accrual: bool | None = None
    requires_approval: bool | None = None
    effective_days_per_year: Decimal | None = None
    effective_accrual_type: Open[PtoAccrualType]
    effective_accrual_schedule: Open[PtoAccrualSchedule] | None = None
    effective_deferred_accrual: bool | None = None
    effective_requires_approval: bool
    holiday_calendar: Ref | None = None
    """Only in bulk results."""
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None


class PtoAllocationReset(HarvestModel):
    """What Harvest returns when an update leaves no override behind."""

    user: Ref
    pto_type: PtoTypeRef
    year: int
    customized: bool
    message: str


class PtoAllocationOutcome(RootModel[PtoAllocation | PtoAllocationReset]):
    """Each shape lacks a key the other requires, so the union picks by
    shape."""


class PtoAllocationUpdate(HarvestInput):
    """Values equal to the policy defaults remove the override, as
    ``reset_to_default=True`` does."""

    user_id: int
    pto_type_id: int
    year: int | None = None
    accrual_type: PtoAccrualType | None = None
    accrual_schedule: PtoAccrualSchedule | None = None
    accrual_first_payday: dt.date | None = None
    accrual_leave_hours: float | None = None
    accrual_worked_hours: float | None = None
    accrual_max_hours_per_year: float | None = None
    days_per_year: float | None = None
    carryover_days: float | None = None
    requires_approval: bool | None = None
    reset_to_default: bool | None = None


class PtoAllocationBulkItem(HarvestInput):
    """An explicit None clears an override, except ``carryover_days``,
    which Harvest clears with 0."""

    user_id: int
    pto_type_id: int
    year: int
    accrual_type: PtoAccrualType | None = None
    accrual_schedule: PtoAccrualSchedule | None = None
    accrual_first_payday: dt.date | None = None
    accrual_leave_hours: float | None = None
    accrual_worked_hours: float | None = None
    accrual_max_hours_per_year: float | None = None
    days_per_year: float | None = None
    carryover_days: float | None = None
    deferred_accrual: bool | None = None
    requires_approval: bool | None = None
    reset_to_default: bool | None = None
    holiday_calendar_id: int | Literal["none"] | None = None
    """Also assigns the user's holiday calendar; None or "none" clears it."""


class PtoAllocationBulkUpdate(HarvestInput):
    allocations: list[PtoAllocationBulkItem]


class PtoAllocationBulkResult(HarvestModel):
    pto_allocations: list[PtoAllocation]
