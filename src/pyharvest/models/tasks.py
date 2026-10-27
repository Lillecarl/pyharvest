from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pyharvest.models.base import HarvestInput, HarvestModel


class Task(HarvestModel):
    id: int
    name: str
    billable_by_default: bool
    default_hourly_rate: Decimal | None = None
    is_default: bool
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime


class TaskCreate(HarvestInput):
    name: str
    billable_by_default: bool | None = None
    default_hourly_rate: float | None = None
    is_default: bool | None = None
    is_active: bool | None = None


class TaskUpdate(HarvestInput):
    name: str | None = None
    billable_by_default: bool | None = None
    default_hourly_rate: float | None = None
    is_default: bool | None = None
    is_active: bool | None = None
