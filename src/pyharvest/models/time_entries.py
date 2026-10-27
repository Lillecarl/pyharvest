from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum

from pyharvest.models.base import HarvestModel, Ref


class ApprovalStatus(StrEnum):
    UNSUBMITTED = "unsubmitted"
    SUBMITTED = "submitted"
    APPROVED = "approved"


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


class ExternalReferenceInput(HarvestModel):
    id: str
    group_id: str | None = None
    account_id: str | None = None
    permalink: str | None = None


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
    approval_status: ApprovalStatus
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
