from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pyharvest.models.base import (
    ApprovalStatus,
    HarvestInput,
    HarvestModel,
    Open,
    Ref,
)


class TimeEntryClient(Ref):
    currency: str | None = None


class TimeEntryProject(Ref):
    code: str | None = None


class TimeEntryInvoice(HarvestModel):
    id: int
    number: str


class ExternalReference(HarvestModel):
    id: str
    group_id: str | None = None
    account_id: str | None = None
    permalink: str | None = None
    service: str | None = None
    service_icon_url: str | None = None


class ExternalReferenceInput(HarvestInput):
    id: str
    group_id: str | None = None
    account_id: str | None = None
    permalink: str | None = None


class TimeEntryCreate(HarvestInput):
    """Pass ``hours`` on accounts that track duration, ``started_time`` and
    ``ended_time`` on accounts that track start and end times. Leaving both
    out starts a timer."""

    project_id: int
    task_id: int
    spent_date: dt.date
    user_id: int | None = None
    hours: float | None = None
    started_time: str | None = None
    ended_time: str | None = None
    notes: str | None = None
    external_reference: ExternalReferenceInput | None = None


class TimeEntryUpdate(HarvestInput):
    project_id: int | None = None
    task_id: int | None = None
    spent_date: dt.date | None = None
    hours: float | None = None
    started_time: str | None = None
    ended_time: str | None = None
    notes: str | None = None
    external_reference: ExternalReferenceInput | None = None


class TimeEntryUserAssignment(HarvestModel):
    id: int
    is_project_manager: bool
    is_active: bool
    use_default_rates: bool | None = None
    budget: Decimal | None = None
    hourly_rate: Decimal | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class TimeEntryTaskAssignment(HarvestModel):
    id: int
    billable: bool
    is_active: bool
    budget: Decimal | None = None
    hourly_rate: Decimal | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class TimeEntry(HarvestModel):
    id: int
    spent_date: dt.date
    user: Ref
    user_assignment: TimeEntryUserAssignment | None = None
    client: TimeEntryClient
    project: TimeEntryProject
    task: Ref
    task_assignment: TimeEntryTaskAssignment | None = None
    external_reference: ExternalReference | None = None
    invoice: TimeEntryInvoice | None = None
    hours: Decimal
    hours_without_timer: Decimal
    rounded_hours: Decimal
    notes: str | None = None
    is_locked: bool
    is_explicitly_locked: bool | None = None
    locked_reason: str | None = None
    is_closed: bool
    """Deprecated by Harvest: read ``approval_status``."""
    approval_status: Open[ApprovalStatus]
    is_billed: bool
    timer_started_at: dt.datetime | None = None
    # A string in the account's clock format, "14:59" or "2:59pm".
    started_time: str | None = None
    ended_time: str | None = None
    is_running: bool
    billable: bool
    budgeted: bool
    billable_rate: Decimal | None = None
    cost_rate: Decimal | None = None
    created_at: dt.datetime
    updated_at: dt.datetime
