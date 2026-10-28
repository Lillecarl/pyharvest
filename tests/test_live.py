"""Read-only checks against a real Harvest account.

Skipped unless HARVEST_TOKEN and HARVEST_ACCOUNT are set, so the Nix build
(no network) never runs them. They only GET: the account holds real data.
"""

from __future__ import annotations

import datetime as dt
import os
import types
import typing
from typing import TYPE_CHECKING, Any

import pytest
from mcp import Client as McpClient
from pydantic import BaseModel

from pyharvest import ForbiddenError, Harvest
from pyharvest.mcp import create_server, harvest_from_env
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
    from collections.abc import AsyncIterator

    from pyharvest._session import QueryValue

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.skipif(
        not (os.environ.get("HARVEST_TOKEN") and os.environ.get("HARVEST_ACCOUNT")),
        reason="needs HARVEST_TOKEN and HARVEST_ACCOUNT",
    ),
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


@pytest.fixture
async def harvest() -> AsyncIterator[Harvest]:
    async with Harvest.from_env(user_agent="pyharvest live tests") as harvest:
        yield harvest


async def raw_list(
    harvest: Harvest, path: str, key: str, params: dict[str, QueryValue]
) -> list[Any]:
    response = await harvest._session.request(
        "GET", path, params={"per_page": 100, **params}
    )
    records = response.json()[key]
    if not records:
        pytest.skip(f"{path}: no records to check")
    return records


# Reports reject ranges over a year; keep it recent and cheap (the reports
# rate limit is 100 requests per 15 minutes).
_TODAY = dt.date.today()
_RECENT: dict[str, QueryValue] = {"from": _TODAY - dt.timedelta(days=90), "to": _TODAY}


@pytest.mark.parametrize(
    ("path", "key", "model", "params"),
    [
        ("clients", "clients", Client, {}),
        ("contacts", "contacts", Contact, {}),
        (
            "estimate_item_categories",
            "estimate_item_categories",
            EstimateItemCategory,
            {},
        ),
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
        (
            "users/me/project_assignments",
            "project_assignments",
            ProjectAssignment,
            {},
        ),
        ("reports/time/projects", "results", TimeByProject, _RECENT),
        ("reports/time/detailed", "results", DetailedTimeRow, _RECENT),
        ("reports/expenses/detailed", "results", DetailedExpenseRow, _RECENT),
    ],
)
async def test_models_cover_live_fields(
    harvest: Harvest,
    path: str,
    key: str,
    model: type[BaseModel],
    params: dict[str, QueryValue],
) -> None:
    try:
        records = await raw_list(harvest, path, key, params)
    except ForbiddenError:
        pytest.skip(f"{path}: this account may not read it")
    assert unmodelled(model, records) == set()
    for record in records:
        model.model_validate(record)


@pytest.mark.parametrize(
    ("path", "model"),
    [
        ("users/me", User),
        ("company", Company),
        ("company/reimbursement_settings", ReimbursementSettings),
        ("notification_preferences", NotificationSettings),
    ],
)
async def test_objects_cover_live_fields(
    harvest: Harvest, path: str, model: type[BaseModel]
) -> None:
    try:
        raw = (await harvest._session.request("GET", path)).json()
    except ForbiddenError:
        pytest.skip(f"{path}: this account may not read it")
    assert unmodelled(model, raw) == set()
    model.model_validate(raw)


async def test_time_entries_paginate(harvest: Harvest) -> None:
    session = harvest._session
    total = (
        await session.request("GET", "time_entries", params={"per_page": 1})
    ).json()["total_entries"]
    if total < 3:
        pytest.skip("needs three time entries to cross pages")
    # Small pages force several links.next hops over the same records.
    ids = [
        e.id
        async for e in session.paginate(
            "time_entries", "time_entries", TimeEntry, params={"per_page": 2}
        )
    ]
    assert len(ids) == total == len(set(ids))


@pytest.mark.parametrize(
    ("tool", "arguments"),
    [
        ("me", {}),
        ("my_projects", {}),
        (
            "time_summary",
            {"from_date": str(_TODAY - dt.timedelta(days=30)), "to_date": str(_TODAY)},
        ),
        ("list_time_entries", {"from_date": str(_TODAY - dt.timedelta(days=7))}),
    ],
)
async def test_mcp_read_tools(tool: str, arguments: dict[str, Any]) -> None:
    async with McpClient(create_server(harvest_from_env)) as client:
        result = await client.call_tool(tool, arguments)
    assert not result.is_error, result.content
