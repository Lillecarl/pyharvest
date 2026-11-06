"""Model coverage checks shared by the live and demo suites."""

from __future__ import annotations

import datetime as dt
import types
import typing
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import BaseModel

from pyharvest import ForbiddenError
from pyharvest.models.clients import Client, Contact
from pyharvest.models.company import Company, ReimbursementSettings
from pyharvest.models.estimates import Estimate, EstimateItemCategory
from pyharvest.models.expenses import Expense, ExpenseCategory
from pyharvest.models.imports import Import
from pyharvest.models.invoices import Invoice, InvoiceItemCategory
from pyharvest.models.notifications import Notification, NotificationSettings
from pyharvest.models.projects import Project, Tag, TaskAssignment, UserAssignment
from pyharvest.models.pto import (
    HolidayCalendar,
    PtoAllocation,
    PtoAssignment,
    TimeOffPolicy,
    TimeOffRequest,
    WorkSchedule,
)
from pyharvest.models.reimbursements import Reimbursement
from pyharvest.models.reports import DetailedExpenseRow, DetailedTimeRow, TimeByProject
from pyharvest.models.roles import CustomRole, Permission, Role
from pyharvest.models.tasks import Task
from pyharvest.models.time_entries import TimeEntry
from pyharvest.models.user_details import ProjectAssignment
from pyharvest.models.users import User

if TYPE_CHECKING:
    from pyharvest import Harvest
    from pyharvest._session import QueryValue

TODAY = dt.date.today()
# Reports reject ranges over a year; keep it recent and cheap (the reports
# rate limit is 100 requests per 15 minutes).
RECENT: dict[str, QueryValue] = {"from": TODAY - dt.timedelta(days=90), "to": TODAY}

LISTS: list[tuple[str, str, type[BaseModel], dict[str, QueryValue]]] = [
    ("clients", "clients", Client, {}),
    ("contacts", "contacts", Contact, {}),
    ("estimate_item_categories", "estimate_item_categories", EstimateItemCategory, {}),
    ("estimates", "estimates", Estimate, {}),
    ("expense_categories", "expense_categories", ExpenseCategory, {}),
    ("expenses", "expenses", Expense, {}),
    ("invoice_item_categories", "invoice_item_categories", InvoiceItemCategory, {}),
    ("invoices", "invoices", Invoice, {}),
    ("custom_roles", "custom_roles", CustomRole, {}),
    ("permissions", "permissions", Permission, {}),
    ("roles", "roles", Role, {}),
    ("projects", "projects", Project, {}),
    ("tags", "tags", Tag, {}),
    ("task_assignments", "task_assignments", TaskAssignment, {}),
    ("tasks", "tasks", Task, {}),
    ("time_entries", "time_entries", TimeEntry, {}),
    ("user_assignments", "user_assignments", UserAssignment, {}),
    ("users", "users", User, {}),
    ("imports", "imports", Import, {}),
    ("notifications", "notifications", Notification, {}),
    ("reimbursements", "reimbursements", Reimbursement, {}),
    ("pto/work_schedules", "pto_work_schedules", WorkSchedule, {}),
    ("pto/requests", "pto_requests", TimeOffRequest, {}),
    ("pto/types", "pto_types", TimeOffPolicy, {}),
    ("pto/holiday_calendars", "pto_holiday_calendars", HolidayCalendar, {}),
    ("pto/assignments", "assignments", PtoAssignment, {}),
    ("pto/allocations", "pto_allocations", PtoAllocation, {}),
    ("users/me/project_assignments", "project_assignments", ProjectAssignment, {}),
    ("reports/time/projects", "results", TimeByProject, RECENT),
    ("reports/time/detailed", "results", DetailedTimeRow, RECENT),
    ("reports/expenses/detailed", "results", DetailedExpenseRow, RECENT),
]

OBJECTS: list[tuple[str, type[BaseModel]]] = [
    ("users/me", User),
    ("company", Company),
    ("company/reimbursement_settings", ReimbursementSettings),
    ("notification_preferences", NotificationSettings),
]


def _model_in(annotation: Any) -> type[BaseModel] | None:
    """The model inside ``M``, ``M | None`` or ``list[M]``, if any."""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation
    if typing.get_origin(annotation) in (typing.Union, types.UnionType, list):
        for arg in typing.get_args(annotation):
            if found := _model_in(arg):
                return found
    return None


def unmodelled(model: type[BaseModel], raw: Any, path: str = "") -> set[str]:
    """Keys in a raw response that the model does not declare, recursively.

    Any: raw is parsed JSON of unknown shape, the input under test.
    """
    if isinstance(raw, list):
        return {k for item in raw for k in unmodelled(model, item, path + "[]")}
    if not isinstance(raw, dict):
        return set()
    missing = {f"{path}.{key}" for key in raw if key not in model.model_fields}
    for name, field in model.model_fields.items():
        nested = _model_in(field.annotation)
        if nested and raw.get(name) is not None:
            missing |= unmodelled(nested, raw[name], f"{path}.{name}")
    return missing


async def check_list(
    harvest: Harvest,
    path: str,
    key: str,
    model: type[BaseModel],
    params: dict[str, QueryValue],
) -> None:
    """Skip when the account may not read the list or it is empty."""
    try:
        response = await harvest._session.request(
            "GET", path, params={"per_page": 100, **params}
        )
    except ForbiddenError as exc:
        pytest.skip(f"{path}: {exc.message}")
    records = response.json()[key]
    if not records:
        pytest.skip(f"{path}: no records to check")
    assert unmodelled(model, records) == set()
    for record in records:
        model.model_validate(record)


async def check_object(harvest: Harvest, path: str, model: type[BaseModel]) -> None:
    try:
        raw = (await harvest._session.request("GET", path)).json()
    except ForbiddenError as exc:
        pytest.skip(f"{path}: {exc.message}")
    assert unmodelled(model, raw) == set()
    model.model_validate(raw)
