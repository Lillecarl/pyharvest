from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.estimates import (
    Estimate,
    EstimateCreate,
    EstimateEventType,
    EstimateItemCategoryCreate,
    EstimateLineItemCreate,
    EstimateLineItemUpdate,
    EstimateMessageCreate,
    EstimateMessageRecipientInput,
    EstimateState,
    EstimateUpdate,
)
from pyharvest.resources.estimates import (
    EstimateItemCategories,
    EstimateMessages,
    Estimates,
)

from . import fixtures, fixtures_estimates

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_list_renders_filters(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("estimates").respond(
        json=fixtures.page("estimates", [fixtures_estimates.estimate()], None)
    )

    estimates = [
        e
        async for e in Estimates(harvest._session).list(
            client_id=2,
            state=EstimateState.SENT,
            from_=dt.date(2024, 3, 1),
            to=dt.date(2024, 3, 31),
        )
    ]

    assert estimates[0].state is EstimateState.DRAFT
    assert estimates[0].line_items[0].quantity == Decimal(1)
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "client_id": "2",
        "state": "sent",
        "from": "2024-03-01",
        "to": "2024-03-31",
    }


@pytest.mark.anyio
async def test_create_sends_line_items(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("estimates").respond(201, json=fixtures_estimates.estimate())

    await Estimates(harvest._session).create(
        EstimateCreate(
            client_id=2,
            subject="Engine",
            line_items=[EstimateLineItemCreate(kind="Service", unit_price=5000.0)],
        )
    )

    assert json.loads(route.calls.last.request.content) == {
        "client_id": 2,
        "subject": "Engine",
        "line_items": [{"kind": "Service", "unit_price": 5000.0}],
    }


@pytest.mark.anyio
async def test_update_line_items_sends_destroy_key(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.patch("estimates/200").respond(json=fixtures_estimates.estimate())

    await Estimates(harvest._session).update(
        200,
        EstimateUpdate(
            notes=None,
            line_items=[
                EstimateLineItemUpdate(id=201, destroy=True),
                EstimateLineItemUpdate(id=202, description="Phase 2"),
                EstimateLineItemUpdate(kind="Product", unit_price=10.0),
            ],
        ),
    )

    assert json.loads(route.calls.last.request.content) == {
        "notes": None,
        "line_items": [
            {"id": 201, "_destroy": True},
            {"id": 202, "description": "Phase 2"},
            {"kind": "Product", "unit_price": 10.0},
        ],
    }


def test_unknown_state_stays_str() -> None:
    estimate = Estimate.model_validate(fixtures_estimates.estimate(state="archived"))

    assert estimate.state == "archived"


@pytest.mark.anyio
async def test_message_create(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("estimates/200/messages").respond(
        201, json=fixtures_estimates.estimate_message(event_type=None)
    )

    message = await EstimateMessages(harvest._session).create(
        200,
        EstimateMessageCreate(
            recipients=[EstimateMessageRecipientInput(email="charles@example.com")],
            subject="Estimate 1001",
            event_type=EstimateEventType.SEND,
        ),
    )

    assert message.event_type is None
    assert json.loads(route.calls.last.request.content) == {
        "recipients": [{"email": "charles@example.com"}],
        "subject": "Estimate 1001",
        "event_type": "send",
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("method", "event_type"),
    [
        ("mark_as_sent", "send"),
        ("mark_as_accepted", "accept"),
        ("mark_as_declined", "decline"),
        ("reopen", "re-open"),
    ],
)
async def test_message_events(
    harvest: Harvest, router: respx.MockRouter, method: str, event_type: str
) -> None:
    route = router.post("estimates/200/messages").respond(
        201, json=fixtures_estimates.estimate_message(event_type=event_type)
    )

    message = await getattr(EstimateMessages(harvest._session), method)(200)

    assert message.event_type == event_type
    assert isinstance(message.event_type, EstimateEventType)
    assert json.loads(route.calls.last.request.content) == {"event_type": event_type}


@pytest.mark.anyio
async def test_message_list_and_delete(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("estimates/200/messages").respond(
        json=fixtures.page(
            "estimate_messages", [fixtures_estimates.estimate_message()], None
        )
    )
    deleted = router.delete("estimates/200/messages/300").respond(200)
    messages = EstimateMessages(harvest._session)

    listed = [m async for m in messages.list(200)]
    await messages.delete(200, 300)

    assert listed[0].id == 300
    assert deleted.called


@pytest.mark.anyio
async def test_item_categories(harvest: Harvest, router: respx.MockRouter) -> None:
    router.get("estimate_item_categories").respond(
        json=fixtures.page(
            "estimate_item_categories",
            [fixtures_estimates.estimate_item_category()],
            None,
        )
    )
    created = router.post("estimate_item_categories").respond(
        201, json=fixtures_estimates.estimate_item_category(name="Hosting")
    )
    categories = EstimateItemCategories(harvest._session)

    listed = [c async for c in categories.list()]
    category = await categories.create(EstimateItemCategoryCreate(name="Hosting"))

    assert listed[0].name == "Service"
    assert category.name == "Hosting"
    assert json.loads(created.calls.last.request.content) == {"name": "Hosting"}
