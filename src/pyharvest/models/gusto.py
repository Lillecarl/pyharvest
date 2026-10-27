from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum

from pyharvest.models.base import HarvestInput, HarvestModel, Open


class GustoSyncRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class GustoWeekday(StrEnum):
    SUNDAY = "Sunday"
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"


class GustoReminderFrequency(StrEnum):
    WEEKLY = "weekly"
    SEMIMONTHLY = "semimonthly"
    MONTHLY = "monthly"


class GustoMonthPosition(StrEnum):
    FIRST_DAY = "first_day"
    FIRST_WEEK = "first_week"
    """The 7th."""
    MID_MONTH = "mid_month"
    """The 15th."""
    LAST_WEEK = "last_week"
    """Seven days before the end of the month."""
    LAST_DAY = "last_day"


class GustoEntityType(StrEnum):
    EMPLOYEE = "Employee"
    CONTRACTOR = "Contractor"


class GustoSyncRun(HarvestModel):
    id: int
    status: Open[GustoSyncRunStatus]
    run_type: str
    date_range_start: dt.date
    date_range_end: dt.date
    gusto_payroll_uuid: str | None = None
    workweek_anchor: Open[GustoWeekday] | None = None
    initiated_by_user_id: int | None = None
    created_at: dt.datetime
    started_at: dt.datetime | None = None
    completed_at: dt.datetime | None = None
    terminal_error_message: str | None = None
    created_count: int
    skipped_count: int
    error_count: int


class GustoJob(HarvestModel):
    uuid: str
    title: str


class GustoPreviewProject(HarvestModel):
    """One teammate and project pair a sync run would post."""

    user_mapping_id: int
    user_id: int
    project_id: int
    # Nine documented states; plain str, as the set grows with Gusto's rules.
    dominant_state: str
    entry_count: int
    total_hours: Decimal
    state_counts: dict[str, int]
    job_required: bool
    suggested_job_uuid: str | None = None
    available_jobs: list[GustoJob]


class GustoSyncPreview(HarvestModel):
    date_range_start: dt.date
    date_range_end: dt.date
    gusto_payroll_uuid: str | None = None
    locked_filtered_count: int
    api_errors: list[str]
    projects: list[GustoPreviewProject]


class GustoSyncRange(HarvestInput):
    """A payroll UUID sets the range from its pay period and overrides the
    dates. With neither, Harvest takes the last seven days."""

    gusto_payroll_uuid: str | None = None
    date_range_start: dt.date | None = None
    date_range_end: dt.date | None = None


class GustoSyncProjectInput(HarvestInput):
    user_mapping_id: int
    project_id: int
    gusto_job_uuid: str | None = None


class GustoSyncRunCreate(GustoSyncRange):
    projects: list[GustoSyncProjectInput]


class GustoSyncReminder(HarvestModel):
    enabled: bool
    frequency: Open[GustoReminderFrequency] | None = None
    weekday: Open[GustoWeekday] | None = None
    monthly_position: Open[GustoMonthPosition] | None = None
    semimonthly_position_one: Open[GustoMonthPosition] | None = None
    semimonthly_position_two: Open[GustoMonthPosition] | None = None


class GustoUserMapping(HarvestModel):
    id: int
    user_id: int
    gusto_entity_type: Open[GustoEntityType]
    gusto_entity_uuid: str


class GustoSettings(HarvestModel):
    connected: bool
    needs_reconnect: bool
    gusto_company_name: str | None = None
    workweek_anchor: Open[GustoWeekday] | None = None
    workweek_anchor_editable: bool
    sync_reminder: GustoSyncReminder
    user_mappings: list[GustoUserMapping]


class GustoSyncReminderInput(HarvestInput):
    """Replaces the stored reminder whole. ``enabled=False`` alone clears the
    cadence."""

    enabled: bool
    frequency: GustoReminderFrequency | None = None
    weekday: GustoWeekday | None = None
    monthly_position: GustoMonthPosition | None = None
    semimonthly_position_one: GustoMonthPosition | None = None
    semimonthly_position_two: GustoMonthPosition | None = None


class GustoSettingsUpdate(HarvestInput):
    workweek_anchor: GustoWeekday
    sync_reminder: GustoSyncReminderInput | None = None
    """Leave unset to keep the stored reminder."""


class GustoUserMappingCreate(HarvestInput):
    user_id: int
    gusto_entity_type: GustoEntityType
    gusto_entity_uuid: str


class GustoUserMappingBulkCreate(HarvestInput):
    mappings: list[GustoUserMappingCreate]


class GustoUserMappingFailure(HarvestModel):
    user_id: int | None = None
    message: str


class GustoUserMappingBulkResult(HarvestModel):
    """Each mapping is created on its own, so some may fail."""

    created_count: int
    created: list[GustoUserMapping]
    failed: list[GustoUserMappingFailure]
