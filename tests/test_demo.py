"""Write tests against a Harvest trial account.

Opt-in: `pytest -m demo`. Credentials come from `.demoenv` in the repository
root, or the file `HARVEST_ENV_FILE` names; never from the environment, which
direnv fills with the real account. The `demo` fixture refuses any company
whose plan is not a trial.

`seed` builds one record of each kind, so the coverage checks have data, and
deletes it all at the end. Every record is named with PREFIX: after a crash,
search for it to clean up by hand.
"""

from __future__ import annotations

import datetime as dt
import os
import uuid
from contextlib import AsyncExitStack
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from pyharvest import Attachment, Harvest, NotFoundError
from pyharvest.client import read_env_file
from pyharvest.models.approvals import ApprovalBucket, ApprovalSubmit
from pyharvest.models.base import ApprovalStatus
from pyharvest.models.clients import ClientCreate, ContactCreate
from pyharvest.models.estimates import (
    EstimateCreate,
    EstimateItemCategoryCreate,
    EstimateLineItemCreate,
)
from pyharvest.models.expenses import ExpenseCategoryCreate, ExpenseCreate
from pyharvest.models.invoices import (
    InvoiceCreate,
    InvoiceItemCategoryCreate,
    InvoiceLineItemCreate,
    InvoicePaymentCreate,
)
from pyharvest.models.projects import (
    BillBy,
    BudgetBy,
    ProjectCreate,
    TaskAssignmentCreate,
    UserAssignmentCreate,
)
from pyharvest.models.roles import CustomRoleCreate, RoleCreate
from pyharvest.models.tasks import TaskCreate, TaskUpdate
from pyharvest.models.time_entries import TimeEntry, TimeEntryCreate
from pyharvest.models.user_details import (
    BillableRate,
    CostRate,
    ProjectAssignment,
    Teammate,
    TeammatesUpdate,
    UserRateCreate,
)
from pyharvest.models.users import UserCreate, UserUpdate

from . import livecheck

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable

    from pydantic import BaseModel

    from pyharvest._session import QueryValue

pytestmark = [pytest.mark.anyio, pytest.mark.demo]

ENV_FILE = Path(
    os.environ.get("HARVEST_ENV_FILE", Path(__file__).parent.parent / ".demoenv")
)
PREFIX = "pyharvest-test"
# Monday of last week: a closed week, so approvals can take it.
WEEK = livecheck.TODAY - dt.timedelta(days=livecheck.TODAY.weekday() + 7)


RECEIPT = Attachment("receipt.pdf", b"%PDF-1.4\n%%EOF\n", "application/pdf")


def name(kind: str) -> str:
    """A unique name a leftover record can be found and removed by."""
    return f"{PREFIX} {kind} {uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
async def demo() -> AsyncIterator[Harvest]:
    if not ENV_FILE.is_file():
        pytest.skip(f"no {ENV_FILE}")
    env = read_env_file(ENV_FILE)
    async with Harvest(
        access_token=env["HARVEST_TOKEN"],
        account_id=env["HARVEST_ACCOUNT"],
        user_agent="pyharvest demo tests",
    ) as harvest:
        company = await harvest.company.get()
        if company.plan_type != "trial":
            pytest.fail(f"{ENV_FILE} is {company.name!r}, plan {company.plan_type!r}")
        yield harvest


@dataclass(frozen=True, slots=True)
class Seed:
    user_id: int
    client_id: int
    project_id: int
    task_id: int
    entries: list[TimeEntry]


def _cleanup[**P](
    stack: AsyncExitStack, delete: Callable[P, Awaitable[Any]], *args: P.args
) -> None:
    """Delete on exit; a record already gone with its parent is fine."""

    async def run() -> None:
        try:
            await delete(*args)
        except NotFoundError:
            pass

    stack.push_async_callback(run)


@pytest.fixture(scope="module")
async def seed(demo: Harvest) -> AsyncIterator[Seed]:
    async with AsyncExitStack() as stack:
        me = await demo.users.me()
        client = await demo.clients.create(ClientCreate(name=name("client")))
        _cleanup(stack, demo.clients.delete, client.id)
        contact = await demo.contacts.create(
            ContactCreate(client_id=client.id, first_name=name("contact"))
        )
        _cleanup(stack, demo.contacts.delete, contact.id)

        # Harvest never deletes a task or expense category once time or an
        # expense used it, so the seed borrows the account's own.
        task = await anext(demo.tasks.list(is_active=True))
        category = await anext(demo.expense_categories.list(is_active=True))
        project = await demo.projects.create(
            ProjectCreate(
                client_id=client.id,
                name=name("project"),
                is_billable=True,
                bill_by=BillBy.PROJECT,
                budget_by=BudgetBy.PROJECT,
                hourly_rate=1000,
                budget=100,
            )
        )
        # Registered after the client, so it runs first: a client with a
        # project cannot be deleted. The project takes its entries along.
        _cleanup(stack, demo.projects.delete, project.id)
        assigned = {
            a.user.id async for a in demo.user_assignments.list(project_id=project.id)
        }
        if me.id not in assigned:
            await demo.user_assignments.create(
                project.id, UserAssignmentCreate(user_id=me.id)
            )
        await demo.task_assignments.create(
            project.id, TaskAssignmentCreate(task_id=task.id, billable=True)
        )
        entries = [
            await demo.time_entries.create(
                TimeEntryCreate(
                    project_id=project.id,
                    task_id=task.id,
                    spent_date=WEEK + dt.timedelta(days=day),
                    hours=1.5 + day,
                    notes=name("entry"),
                )
            )
            for day in range(3)
        ]

        expense = await demo.expenses.create(
            ExpenseCreate(
                project_id=project.id,
                expense_category_id=category.id,
                spent_date=WEEK,
                total_cost=123.45,
                notes=name("expense"),
            ),
            receipt=RECEIPT,
        )
        _cleanup(stack, demo.expenses.delete, expense.id)

        estimate_kind = await demo.estimate_item_categories.create(
            EstimateItemCategoryCreate(name=name("estimate kind"))
        )
        _cleanup(stack, demo.estimate_item_categories.delete, estimate_kind.id)
        estimate = await demo.estimates.create(
            EstimateCreate(
                client_id=client.id,
                subject=name("estimate"),
                line_items=[
                    EstimateLineItemCreate(
                        kind=estimate_kind.name, unit_price=500, quantity=2
                    )
                ],
            )
        )
        _cleanup(stack, demo.estimates.delete, estimate.id)

        invoice_kind = await demo.invoice_item_categories.create(
            InvoiceItemCategoryCreate(name=name("invoice kind"))
        )
        _cleanup(stack, demo.invoice_item_categories.delete, invoice_kind.id)
        invoice = await demo.invoices.create(
            InvoiceCreate(
                client_id=client.id,
                subject=name("invoice"),
                line_items=[
                    InvoiceLineItemCreate(
                        kind=invoice_kind.name,
                        unit_price=750,
                        quantity=1,
                        project_id=project.id,
                    )
                ],
            )
        )
        _cleanup(stack, demo.invoices.delete, invoice.id)
        await demo.invoice_payments.create(
            invoice.id, InvoicePaymentCreate(amount=100, paid_date=WEEK)
        )

        role = await demo.roles.create(RoleCreate(name=name("role"), user_ids=[me.id]))
        _cleanup(stack, demo.roles.delete, role.id)
        permission = await anext(demo.permissions.list())
        custom = await demo.custom_roles.create(
            CustomRoleCreate(name=name("custom role"), permission_ids=[permission.id])
        )
        _cleanup(stack, demo.custom_roles.delete, custom.id)

        yield Seed(
            user_id=me.id,
            client_id=client.id,
            project_id=project.id,
            task_id=task.id,
            entries=entries,
        )


@pytest.mark.parametrize(("path", "key", "model", "params"), livecheck.LISTS)
async def test_models_cover_demo_fields(
    demo: Harvest,
    seed: Seed,
    path: str,
    key: str,
    model: type[BaseModel],
    params: dict[str, QueryValue],
) -> None:
    await livecheck.check_list(demo, path, key, model, params)


@pytest.mark.parametrize(("path", "model"), livecheck.OBJECTS)
async def test_objects_cover_demo_fields(
    demo: Harvest, path: str, model: type[BaseModel]
) -> None:
    await livecheck.check_object(demo, path, model)


async def test_time_entries_paginate(demo: Harvest, seed: Seed) -> None:
    ids = [
        e.id
        async for e in demo._session.paginate(
            "time_entries",
            "time_entries",
            TimeEntry,
            params={"per_page": 2, "project_id": seed.project_id},
        )
    ]
    assert sorted(ids) == sorted(e.id for e in seed.entries)


async def test_detailed_totals_match_rows(demo: Harvest, seed: Seed) -> None:
    end = WEEK + dt.timedelta(days=6)
    rows = [
        r
        async for r in demo.reports.time_detailed(
            from_=WEEK, to=end, project_id=seed.project_id
        )
    ]
    time = await demo.reports.time_detailed_totals(
        from_=WEEK, to=end, project_id=seed.project_id
    )
    [expense] = await demo.reports.expenses_detailed_totals(
        from_=WEEK, to=end, project_id=seed.project_id
    )

    assert time.total_hours == sum(r.hours for r in rows) == Decimal("7.5")
    assert expense.total_amount == Decimal("123.45")


async def test_submit_approve_withdraw(demo: Harvest, seed: Seed) -> None:
    end = WEEK + dt.timedelta(days=6)
    submission = await demo.approvals.submit(
        ApprovalSubmit(period_start=WEEK, period_end=end)
    )
    assert submission.status == "submitted"
    submitted = [
        a.user_id
        async for a in demo.approvals.list(
            WEEK, end, approval_status=ApprovalBucket.SUBMITTED
        )
    ]
    assert seed.user_id in submitted

    [expense] = [e async for e in demo.expenses.list(project_id=seed.project_id)]
    approved = await demo.expenses.approve(expense.id)
    assert approved.approval_status == ApprovalStatus.APPROVED
    same_day = await demo.time_entries.get(seed.entries[0].id)
    assert same_day.approval_status == ApprovalStatus.APPROVED

    # Withdraw takes back the approval, not the submission.
    withdrawn = await demo.expenses.withdraw(expense.id)
    assert withdrawn.approval_status == ApprovalStatus.SUBMITTED
    same_day = await demo.time_entries.get(seed.entries[0].id)
    assert same_day.approval_status == ApprovalStatus.SUBMITTED


async def test_user_round_trip(demo: Harvest, seed: Seed) -> None:
    # Harvest mails an invitation: plus-address the demo owner's own inbox.
    owner = await demo.users.me()
    local, domain = owner.email.split("@")
    tag = uuid.uuid4().hex[:8]
    user = await demo.users.create(
        UserCreate(
            first_name=PREFIX,
            last_name=f"user {tag}",
            email=f"{local}+{PREFIX}-{tag}@{domain}",
            # Accounts on Harvest's new roles refuse "manager".
            access_roles=["project_manager"],
        )
    )
    try:
        changed = await demo.users.update(
            user.id, UserUpdate(weekly_capacity=72000, roles=["Tester"])
        )
        assert (changed.weekly_capacity, list(changed.roles)) == (72000, ["Tester"])

        await demo.user_billable_rates.create(
            user.id, UserRateCreate(amount=950, start_date=WEEK)
        )
        await demo.user_cost_rates.create(user.id, UserRateCreate(amount=400))
        for path, key, model in [
            (f"users/{user.id}/billable_rates", "billable_rates", BillableRate),
            (f"users/{user.id}/cost_rates", "cost_rates", CostRate),
        ]:
            await livecheck.check_list(demo, path, key, model, {})

        teammates = await demo.user_teammates.update(
            user.id, TeammatesUpdate(teammate_ids=[owner.id])
        )
        assert [t.id for t in teammates] == [owner.id]
        await livecheck.check_list(
            demo, f"users/{user.id}/teammates", "teammates", Teammate, {}
        )

        await demo.user_assignments.create(
            seed.project_id, UserAssignmentCreate(user_id=user.id)
        )
        await livecheck.check_list(
            demo,
            f"users/{user.id}/project_assignments",
            "project_assignments",
            ProjectAssignment,
            {},
        )
    finally:
        await demo.users.delete(user.id)


async def test_task_round_trip(demo: Harvest) -> None:
    task = await demo.tasks.create(TaskCreate(name=name("task")))
    try:
        changed = await demo.tasks.update(task.id, TaskUpdate(is_active=False))
        assert not changed.is_active
    finally:
        await demo.tasks.delete(task.id)


async def test_expense_category_round_trip(demo: Harvest) -> None:
    category = await demo.expense_categories.create(
        ExpenseCategoryCreate(name=name("category"), unit_name="km", unit_price=2.5)
    )
    try:
        assert category.unit_price == Decimal("2.5")
    finally:
        await demo.expense_categories.delete(category.id)


async def test_receipt_round_trip(demo: Harvest, seed: Seed) -> None:
    [expense] = [e async for e in demo.expenses.list(project_id=seed.project_id)]
    assert await demo.expenses.download_receipt(expense.id) == RECEIPT
