from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pyharvest.models.base import HarvestInput, HarvestModel, Ref


class Teammate(HarvestModel):
    id: int
    first_name: str
    last_name: str
    email: str


class Teammates(HarvestModel):
    """The unpaginated body of ``PATCH /users/{id}/teammates``."""

    teammates: list[Teammate]


class TeammatesUpdate(HarvestInput):
    """The full set: IDs left out are unassigned, ``[]`` unassigns everyone."""

    teammate_ids: list[int]


class _UserRate(HarvestModel):
    id: int
    amount: Decimal
    # Documented as always set; no live sample, and a rate created without
    # start_date may still come back null.
    start_date: dt.date | None = None
    end_date: dt.date | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class BillableRate(_UserRate):
    pass


class CostRate(_UserRate):
    pass


class UserRateCreate(HarvestInput):
    """Without ``start_date`` the new rate replaces every existing one."""

    amount: float
    start_date: dt.date | None = None


class ProjectAssignmentProject(Ref):
    code: str | None = None
    is_billable: bool | None = None


class ProjectAssignmentClient(Ref):
    currency: str | None = None


class ProjectAssignmentTask(HarvestModel):
    id: int
    billable: bool
    is_active: bool
    hourly_rate: Decimal | None = None
    budget: Decimal | None = None
    task: Ref
    created_at: dt.datetime
    updated_at: dt.datetime


class ProjectAssignment(HarvestModel):
    id: int
    is_project_manager: bool
    is_active: bool
    use_default_rates: bool
    hourly_rate: Decimal | None = None
    budget: Decimal | None = None
    project: ProjectAssignmentProject
    client: ProjectAssignmentClient
    task_assignments: list[ProjectAssignmentTask]
    created_at: dt.datetime
    updated_at: dt.datetime
