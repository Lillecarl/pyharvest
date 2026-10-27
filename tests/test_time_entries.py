from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal

import pytest
import respx

from pyharvest import Harvest
from pyharvest.models import ApprovalStatus, ExternalReferenceInput

from . import fixtures


@pytest.mark.anyio
async def test_list_renders_filters(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("time_entries").respond(
        json=fixtures.page("time_entries", [fixtures.time_entry()], None)
    )

    entries = [
        e
        async for e in harvest.time_entries.list(
            is_billed=False,
            approval_status=ApprovalStatus.APPROVED,
            updated_since=dt.datetime(
                2024, 3, 1, 12, tzinfo=dt.timezone(dt.timedelta(hours=1))
            ),
            from_=dt.date(2024, 3, 1),
            to=dt.date(2024, 3, 31),
        )
    ]

    assert entries[0].hours == Decimal("2.11")
    assert entries[0].approval_status is ApprovalStatus.UNSUBMITTED
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "is_billed": "false",
        "approval_status": "approved",
        "updated_since": "2024-03-01T11:00:00Z",
        "from": "2024-03-01",
        "to": "2024-03-31",
    }


@pytest.mark.anyio
async def test_create_sends_only_set_fields(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("time_entries").respond(201, json=fixtures.time_entry())

    await harvest.time_entries.create(
        project_id=3,
        task_id=4,
        spent_date=dt.date(2024, 3, 1),
        hours=Decimal("1.5"),
        external_reference=ExternalReferenceInput(id="ext-1", permalink="https://x"),
    )

    assert json.loads(route.calls.last.request.content) == {
        "project_id": 3,
        "task_id": 4,
        "spent_date": "2024-03-01",
        "hours": 1.5,
        "external_reference": {"id": "ext-1", "permalink": "https://x"},
    }


@pytest.mark.anyio
async def test_stop(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.patch("time_entries/100/stop").respond(json=fixtures.time_entry())

    entry = await harvest.time_entries.stop(100)

    assert entry.id == 100
    assert route.called
