from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from pyharvest.models.base import HarvestInput, HarvestModel, Open, Ref


class BillBy(StrEnum):
    PROJECT = "Project"
    TASKS = "Tasks"
    PEOPLE = "People"
    NONE = "none"


class BudgetBy(StrEnum):
    PROJECT = "project"
    """Hours per project."""
    PROJECT_COST = "project_cost"
    """Total project fees."""
    TASK = "task"
    """Hours per task."""
    TASK_FEES = "task_fees"
    """Fees per task."""
    PERSON = "person"
    """Hours per person."""
    NONE = "none"


class ProjectClient(Ref):
    currency: str | None = None


class Project(HarvestModel):
    id: int
    client: ProjectClient
    name: str
    code: str | None = None
    currency: str
    is_active: bool
    is_billable: bool
    is_fixed_fee: bool
    bill_by: Open[BillBy]
    hourly_rate: Decimal | None = None
    budget_by: Open[BudgetBy]
    budget_is_monthly: bool
    budget: Decimal | None = None
    """Hours. With ``budget_by`` task or person, the read-only sum of the
    assignments' budgets."""
    cost_budget: Decimal | None = None
    cost_budget_include_expenses: bool
    notify_when_over_budget: bool
    over_budget_notification_percentage: Decimal | None = None
    over_budget_notification_date: dt.date | None = None
    show_budget_to_all: bool
    fee: Decimal | None = None
    notes: str | None = None
    starts_on: dt.date | None = None
    ends_on: dt.date | None = None
    # Beta: empty, per the docs, when the account has no project tags.
    tags: list[Ref] = Field(default_factory=list)
    created_at: dt.datetime
    updated_at: dt.datetime


class ProjectCreate(HarvestInput):
    client_id: int
    name: str
    is_billable: bool
    bill_by: BillBy
    budget_by: BudgetBy
    code: str | None = None
    currency: str | None = None
    is_active: bool | None = None
    is_fixed_fee: bool | None = None
    hourly_rate: float | None = None
    budget_is_monthly: bool | None = None
    budget: float | None = None
    cost_budget: float | None = None
    cost_budget_include_expenses: bool | None = None
    notify_when_over_budget: bool | None = None
    over_budget_notification_percentage: float | None = None
    show_budget_to_all: bool | None = None
    fee: float | None = None
    notes: str | None = None
    starts_on: dt.date | None = None
    ends_on: dt.date | None = None


class ProjectUpdate(HarvestInput):
    client_id: int | None = None
    name: str | None = None
    code: str | None = None
    currency: str | None = None
    """``None`` makes the project follow the client's currency again."""
    is_active: bool | None = None
    is_billable: bool | None = None
    is_fixed_fee: bool | None = None
    bill_by: BillBy | None = None
    hourly_rate: float | None = None
    budget_by: BudgetBy | None = None
    budget_is_monthly: bool | None = None
    budget: float | None = None
    cost_budget: float | None = None
    cost_budget_include_expenses: bool | None = None
    notify_when_over_budget: bool | None = None
    over_budget_notification_percentage: float | None = None
    show_budget_to_all: bool | None = None
    fee: float | None = None
    notes: str | None = None
    starts_on: dt.date | None = None
    ends_on: dt.date | None = None
    tag_ids: list[int] | None = None
    """The complete tag set: ``[]`` clears it, ``None`` leaves it unchanged."""


class AssignmentProject(Ref):
    code: str | None = None


class UserAssignment(HarvestModel):
    id: int
    project: AssignmentProject
    user: Ref
    is_active: bool
    is_project_manager: bool
    use_default_rates: bool | None = None
    hourly_rate: Decimal | None = None
    budget: Decimal | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class UserAssignmentCreate(HarvestInput):
    user_id: int
    is_active: bool | None = None
    is_project_manager: bool | None = None
    use_default_rates: bool | None = None
    hourly_rate: float | None = None
    budget: float | None = None


class UserAssignmentUpdate(HarvestInput):
    is_active: bool | None = None
    is_project_manager: bool | None = None
    use_default_rates: bool | None = None
    hourly_rate: float | None = None
    budget: float | None = None


class TaskAssignment(HarvestModel):
    id: int
    project: AssignmentProject
    task: Ref
    is_active: bool
    billable: bool
    hourly_rate: Decimal | None = None
    budget: Decimal | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class TaskAssignmentCreate(HarvestInput):
    task_id: int
    is_active: bool | None = None
    billable: bool | None = None
    hourly_rate: float | None = None
    budget: float | None = None


class TaskAssignmentUpdate(HarvestInput):
    is_active: bool | None = None
    billable: bool | None = None
    hourly_rate: float | None = None
    budget: float | None = None


class Tag(HarvestModel):
    id: int
    name: str
    created_at: dt.datetime
    updated_at: dt.datetime
