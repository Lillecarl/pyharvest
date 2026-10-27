from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum

from pyharvest.models.base import HarvestInput, HarvestModel


class ApprovalBucket(StrEnum):
    """The ``approval_status`` an approvals listing reports on.

    Harvest refuses ``unsubmitted`` here for now.
    """

    SUBMITTED = "submitted"
    APPROVED = "approved"


class ApprovalExpenseTotal(HarvestModel):
    currency: str
    total_amount: Decimal
    billable_amount: Decimal


class Approval(HarvestModel):
    """One user's time and expenses for a period and bucket."""

    user_id: int
    user_name: str
    avatar_url: str | None = None
    total_hours: Decimal
    billable_hours: Decimal
    has_running_timer: bool
    expenses_by_currency: list[ApprovalExpenseTotal]


class ApprovalSubmit(HarvestInput):
    period_start: dt.date
    period_end: dt.date
    user_id: int | None = None
    """Defaults to the authenticated user."""


class ApprovalSubmission(HarvestModel):
    user_id: int
    period_start: dt.date
    period_end: dt.date
    status: str
    """An acknowledgement, not the period's approval state."""
    timesheet_version: str | None = None
