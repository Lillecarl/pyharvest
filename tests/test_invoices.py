from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.invoices import (
    ExpenseSummaryType,
    Invoice,
    InvoiceCreate,
    InvoiceExpenseImport,
    InvoiceImportCreate,
    InvoiceItemCategoryCreate,
    InvoiceLineItemCreate,
    InvoiceLineItemsImport,
    InvoiceLineItemUpdate,
    InvoiceMessageCreate,
    InvoiceMessageEventType,
    InvoiceMessageRecipientInput,
    InvoicePaymentCreate,
    InvoiceState,
    InvoiceTimeImport,
    InvoiceUpdate,
    PaymentTerm,
    TimeSummaryType,
)
from pyharvest.resources.invoices import (
    InvoiceItemCategories,
    InvoiceMessages,
    InvoicePayments,
    Invoices,
)

from . import fixtures, fixtures_invoices

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


def body(route: respx.Route) -> object:
    return json.loads(route.calls.last.request.content)


@pytest.mark.anyio
async def test_list_renders_filters(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("invoices").respond(
        json=fixtures.page("invoices", [fixtures_invoices.invoice()], None)
    )

    invoices = [
        i
        async for i in Invoices(harvest._session).list(
            client_id=2,
            state=InvoiceState.OPEN,
            from_=dt.date(2024, 4, 1),
            to=dt.date(2024, 4, 30),
        )
    ]

    assert invoices[0].state is InvoiceState.OPEN
    assert invoices[0].payment_term is PaymentTerm.NET_15
    assert invoices[0].line_items[0].amount == Decimal("300.0")
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "client_id": "2",
        "state": "open",
        "from": "2024-04-01",
        "to": "2024-04-30",
    }


@pytest.mark.anyio
async def test_create_free_form(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("invoices").respond(201, json=fixtures_invoices.invoice())

    await Invoices(harvest._session).create(
        InvoiceCreate(
            client_id=2,
            payment_term=PaymentTerm.UPON_RECEIPT,
            line_items=[
                InvoiceLineItemCreate(kind="Service", unit_price=5000.0, project_id=3)
            ],
        )
    )

    assert body(route) == {
        "client_id": 2,
        "payment_term": "upon receipt",
        "line_items": [{"kind": "Service", "unit_price": 5000.0, "project_id": 3}],
    }


@pytest.mark.anyio
async def test_create_from_tracked_time(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("invoices").respond(201, json=fixtures_invoices.invoice())

    await Invoices(harvest._session).create(
        InvoiceImportCreate(
            client_id=2,
            line_items_import=InvoiceLineItemsImport(
                project_ids=[3],
                time=InvoiceTimeImport(
                    summary_type=TimeSummaryType.TASK,
                    from_=dt.date(2024, 3, 1),
                    to=dt.date(2024, 3, 31),
                ),
                expenses=InvoiceExpenseImport(
                    summary_type=ExpenseSummaryType.CATEGORY, attach_receipts=True
                ),
            ),
        )
    )

    assert body(route) == {
        "client_id": 2,
        "line_items_import": {
            "project_ids": [3],
            "time": {"summary_type": "task", "from": "2024-03-01", "to": "2024-03-31"},
            "expenses": {"summary_type": "category", "attach_receipts": True},
        },
    }


@pytest.mark.anyio
async def test_update_line_items(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.patch("invoices/500").respond(json=fixtures_invoices.invoice())

    await Invoices(harvest._session).update(
        500,
        InvoiceUpdate(
            notes=None,
            line_items=[
                InvoiceLineItemUpdate(kind="Service", unit_price=10.0),
                InvoiceLineItemUpdate(id=700, description="Phase 2"),
                InvoiceLineItemUpdate(id=701, destroy=True),
            ],
        ),
    )

    assert body(route) == {
        "notes": None,
        "line_items": [
            {"kind": "Service", "unit_price": 10.0},
            {"id": 700, "description": "Phase 2"},
            {"id": 701, "_destroy": True},
        ],
    }


def test_unknown_state_stays_str() -> None:
    invoice = Invoice.model_validate(
        fixtures_invoices.invoice(state="void", payment_term="net 90")
    )

    assert invoice.state == "void"
    assert invoice.payment_term == "net 90"


@pytest.mark.anyio
async def test_message_events(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("invoices/500/messages").respond(
        201, json=fixtures_invoices.invoice_message(event_type="re-open")
    )

    message = await InvoiceMessages(harvest._session).reopen(500)

    assert message.event_type is InvoiceMessageEventType.REOPEN
    assert body(route) == {"event_type": "re-open"}


@pytest.mark.anyio
async def test_message_send(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("invoices/500/messages").respond(
        201, json=fixtures_invoices.invoice_message()
    )

    message = await InvoiceMessages(harvest._session).create(
        500,
        InvoiceMessageCreate(
            recipients=[InvoiceMessageRecipientInput(email="charles@example.com")],
            attach_pdf=True,
        ),
    )

    assert message.event_type is None
    assert body(route) == {
        "recipients": [{"email": "charles@example.com"}],
        "attach_pdf": True,
    }


@pytest.mark.anyio
async def test_message_template(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("invoices/500/messages/new").respond(
        json={
            "invoice_id": 500,
            "subject": "Reminder",
            "body": "Please pay.",
            "reminder": True,
            "thank_you": False,
        }
    )

    template = await InvoiceMessages(harvest._session).template(500, reminder=True)

    assert template.subject == "Reminder"
    assert dict(route.calls.last.request.url.params) == {"reminder": "true"}


@pytest.mark.anyio
async def test_payments(harvest: Harvest, router: respx.MockRouter) -> None:
    listed = router.get("invoices/500/payments").respond(
        json=fixtures.page(
            "invoice_payments", [fixtures_invoices.invoice_payment()], None
        )
    )
    created = router.post("invoices/500/payments").respond(
        201, json=fixtures_invoices.invoice_payment()
    )
    deleted = router.delete("invoices/500/payments/900").respond(200)
    payments = InvoicePayments(harvest._session)

    listed_payments = [p async for p in payments.list(500)]
    await payments.create(
        500,
        InvoicePaymentCreate(
            amount=330.0,
            paid_at=dt.datetime(
                2024, 4, 10, 14, tzinfo=dt.timezone(dt.timedelta(hours=2))
            ),
        ),
    )
    await payments.delete(500, 900)

    assert listed_payments[0].payment_gateway is not None
    assert listed_payments[0].payment_gateway.id is None
    assert listed.called
    assert body(created) == {"amount": 330.0, "paid_at": "2024-04-10T14:00:00+02:00"}
    assert deleted.called


@pytest.mark.anyio
async def test_item_categories(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("invoice_item_categories").respond(
        201, json=fixtures_invoices.invoice_item_category(name="Hosting")
    )

    category = await InvoiceItemCategories(harvest._session).create(
        InvoiceItemCategoryCreate(name="Hosting")
    )

    assert category.name == "Hosting"
    assert body(route) == {"name": "Hosting"}


@pytest.mark.anyio
async def test_e_invoice_status(harvest: Harvest, router: respx.MockRouter) -> None:
    router.get("invoices/500/e_invoice_status").respond(
        json={
            "status": None,
            "submitted_at": None,
            "last_event_at": None,
            "document_id": None,
            "failure_reason": None,
            "eligible": False,
            "blocked_reason": "company_not_enrolled",
        }
    )

    status = await Invoices(harvest._session).e_invoice_status(500)

    assert status.eligible is False
    assert status.blocked_reason == "company_not_enrolled"
