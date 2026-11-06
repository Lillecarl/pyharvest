from __future__ import annotations

import datetime as dt
import email
import json
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from pyharvest import Attachment, HarvestError
from pyharvest.models import ApprovalStatus
from pyharvest.models.expenses import (
    Expense,
    ExpenseCategoryUpdate,
    ExpenseCreate,
    ExpenseUpdate,
)
from pyharvest.resources.expenses import ExpenseCategories, Expenses

from . import fixtures, fixtures_expenses

if TYPE_CHECKING:
    from pathlib import Path

    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_list_renders_filters(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("expenses").respond(
        json=fixtures.page("expenses", [fixtures_expenses.expense()], None)
    )

    expenses = [
        e
        async for e in Expenses(harvest._session).list(
            project_id=3,
            is_billed=False,
            approval_status=ApprovalStatus.SUBMITTED,
            updated_since=dt.datetime(2024, 3, 1, 12, tzinfo=dt.UTC),
            from_=dt.date(2024, 3, 1),
            to=dt.date(2024, 3, 31),
        )
    ]

    assert expenses[0].total_cost == Decimal("33.35")
    assert expenses[0].approval_status is ApprovalStatus.UNSUBMITTED
    assert expenses[0].receipt is not None
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "project_id": "3",
        "is_billed": "false",
        "approval_status": "submitted",
        "updated_since": "2024-03-01T12:00:00Z",
        "from": "2024-03-01",
        "to": "2024-03-31",
    }


@pytest.mark.anyio
async def test_create_sends_only_set_fields(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("expenses").respond(201, json=fixtures_expenses.expense())

    await Expenses(harvest._session).create(
        ExpenseCreate(
            project_id=3,
            expense_category_id=7,
            spent_date=dt.date(2024, 3, 1),
            total_cost=13.59,
        )
    )

    assert json.loads(route.calls.last.request.content) == {
        "project_id": 3,
        "expense_category_id": 7,
        "spent_date": "2024-03-01",
        "total_cost": 13.59,
    }


@pytest.mark.anyio
async def test_create_with_receipt_sends_multipart(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("expenses").respond(201, json=fixtures_expenses.expense())

    await Expenses(harvest._session).create(
        ExpenseCreate(
            project_id=3,
            expense_category_id=7,
            spent_date=dt.date(2024, 3, 1),
            total_cost=13.59,
            billable=False,
        ),
        receipt=Attachment("kvitto.pdf", b"%PDF-1.4", "application/pdf"),
    )

    request = route.calls.last.request
    assert request.headers["Content-Type"].startswith("multipart/form-data")
    form = email.message_from_bytes(
        b"Content-Type: "
        + request.headers["Content-Type"].encode()
        + b"\r\n\r\n"
        + request.content
    )
    parts = {p.get_param("name", header="content-disposition"): p for p in form.walk()}
    assert {
        k: parts[k].get_payload() for k in ("project_id", "total_cost", "billable")
    } == {
        "project_id": "3",
        "total_cost": "13.59",
        "billable": "false",
    }
    assert parts["receipt"].get_filename() == "kvitto.pdf"
    assert parts["receipt"].get_content_type() == "application/pdf"
    assert parts["receipt"].get_payload(decode=True) == b"%PDF-1.4"


@pytest.mark.anyio
async def test_receipt_with_null_field_raises(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.patch("expenses/500").respond(json=fixtures_expenses.expense())

    with pytest.raises(ValueError, match="notes"):
        await Expenses(harvest._session).update(
            500,
            ExpenseUpdate(notes=None),
            receipt=Attachment("kvitto.pdf", b"%PDF-1.4", "application/pdf"),
        )


@pytest.mark.anyio
async def test_attachment_read_guesses_type(tmp_path: Path) -> None:
    path = tmp_path / "kvitto.pdf"
    path.write_bytes(b"%PDF-1.4")

    assert await Attachment.read(path) == Attachment(
        "kvitto.pdf", b"%PDF-1.4", "application/pdf"
    )


RECEIPT_URL = "https://acme.harvestapp.com/expenses/500/receipt.pdf"


def with_receipt_url(url: str) -> dict[str, object]:
    return fixtures_expenses.expense(
        receipt={
            "url": url,
            "file_name": "ticket.pdf",
            "file_size": 8,
            "content_type": "application/pdf",
        }
    )


@pytest.mark.anyio
async def test_download_receipt_sends_token_to_harvest(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("expenses/500").respond(json=with_receipt_url(RECEIPT_URL))
    route = router.get(RECEIPT_URL).respond(content=b"%PDF-1.4")

    receipt = await Expenses(harvest._session).download_receipt(500)

    assert receipt == Attachment("ticket.pdf", b"%PDF-1.4", "application/pdf")
    assert route.calls.last.request.headers["Authorization"] == "Bearer tok"


@pytest.mark.anyio
async def test_download_receipt_none_without_receipt(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("expenses/500").respond(json=fixtures_expenses.expense(receipt=None))

    assert await Expenses(harvest._session).download_receipt(500) is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/receipt.pdf",
        "https://harvestapp.com.example.com/receipt.pdf",
        "http://acme.harvestapp.com/expenses/500/receipt.pdf",
    ],
)
async def test_download_receipt_refuses_other_hosts(
    harvest: Harvest, router: respx.MockRouter, url: str
) -> None:
    router.get("expenses/500").respond(json=with_receipt_url(url))

    with pytest.raises(ValueError, match="not a Harvest file URL"):
        await Expenses(harvest._session).download_receipt(500)


@pytest.mark.anyio
async def test_download_receipt_raises_on_redirect(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("expenses/500").respond(json=with_receipt_url(RECEIPT_URL))
    router.get(RECEIPT_URL).respond(302, headers={"Location": "https://login/"})

    with pytest.raises(HarvestError):
        await Expenses(harvest._session).download_receipt(500)


@pytest.mark.anyio
async def test_update_sends_explicit_none_as_null(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.patch("expenses/500").respond(json=fixtures_expenses.expense())

    await Expenses(harvest._session).update(
        500, ExpenseUpdate(notes=None, delete_receipt=True)
    )

    assert json.loads(route.calls.last.request.content) == {
        "notes": None,
        "delete_receipt": True,
    }


@pytest.mark.anyio
@pytest.mark.parametrize("action", ["approve", "withdraw"])
async def test_approval_actions_post_without_body(
    harvest: Harvest, router: respx.MockRouter, action: str
) -> None:
    route = router.post(f"expenses/500/{action}").respond(
        json=fixtures_expenses.expense(approval_status="approved")
    )

    expense = await getattr(Expenses(harvest._session), action)(500)

    assert expense.approval_status is ApprovalStatus.APPROVED
    assert route.calls.last.request.content == b""


def test_receipt_and_invoice_may_be_null() -> None:
    expense = Expense.model_validate(
        fixtures_expenses.expense(
            receipt=None, invoice={"id": 9, "number": "1001"}, units=12.5
        )
    )

    assert expense.receipt is None
    assert expense.invoice is not None
    assert expense.units == Decimal("12.5")


@pytest.mark.anyio
async def test_categories(harvest: Harvest, router: respx.MockRouter) -> None:
    listed_route = router.get("expense_categories").respond(
        json=fixtures.page(
            "expense_categories", [fixtures_expenses.expense_category()], None
        )
    )
    updated = router.patch("expense_categories/7").respond(
        json=fixtures_expenses.expense_category(is_active=False)
    )
    categories = ExpenseCategories(harvest._session)

    listed = [c async for c in categories.list(is_active=True)]
    category = await categories.update(7, ExpenseCategoryUpdate(is_active=False))

    assert listed[0].unit_price == Decimal("0.535")
    assert dict(listed_route.calls.last.request.url.params) == {
        "per_page": "2000",
        "is_active": "true",
    }
    assert category.is_active is False
    assert json.loads(updated.calls.last.request.content) == {"is_active": False}
