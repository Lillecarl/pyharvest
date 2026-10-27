from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum

from pyharvest.models.base import HarvestModel, Open


class ImportType(StrEnum):
    CLIENT = "client"
    CONTACT = "contact"
    EXPENSE = "expense"
    PERSON = "person"
    PROJECT = "project"
    TIMESHEET = "timesheet"


class ImportStatus(StrEnum):
    QUEUED = "queued"
    WORKING = "working"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    REVERTING = "reverting"
    REVERTED = "reverted"
    EXPIRED = "expired"


class Import(HarvestModel):
    """An asynchronous CSV import run."""

    id: int
    import_type: Open[ImportType]
    status: Open[ImportStatus]
    csv_file_name: str
    imported_rows_count: int
    imported_hours: Decimal | None = None
    error_rows_count: int
    csv_errors_available: bool
    created_at: dt.datetime
    updated_at: dt.datetime
    started_at: dt.datetime | None = None
    completed_at: dt.datetime | None = None
    reverted_at: dt.datetime | None = None
