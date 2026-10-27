from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal

import pytest
import respx

from pyharvest import Harvest
from pyharvest.models.tasks import TaskCreate, TaskUpdate
from pyharvest.resources.tasks import Tasks

from . import fixtures, fixtures_tasks


@pytest.mark.anyio
async def test_list_renders_filters(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("tasks").respond(
        json=fixtures.page("tasks", [fixtures_tasks.task()], None)
    )

    tasks = [
        t
        async for t in Tasks(harvest._session).list(
            is_active=True,
            updated_since=dt.datetime(2024, 3, 1, 12, tzinfo=dt.UTC),
        )
    ]

    assert tasks[0].default_hourly_rate == Decimal("100.0")
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "is_active": "true",
        "updated_since": "2024-03-01T12:00:00Z",
    }


@pytest.mark.anyio
async def test_create_sends_only_set_fields(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("tasks").respond(201, json=fixtures_tasks.task())

    await Tasks(harvest._session).create(
        TaskCreate(name="Programming", default_hourly_rate=120.0)
    )

    assert json.loads(route.calls.last.request.content) == {
        "name": "Programming",
        "default_hourly_rate": 120.0,
    }


@pytest.mark.anyio
async def test_update_and_delete(harvest: Harvest, router: respx.MockRouter) -> None:
    patch = router.patch("tasks/4").respond(json=fixtures_tasks.task())
    delete = router.delete("tasks/4").respond(200)
    tasks = Tasks(harvest._session)

    await tasks.update(4, TaskUpdate(is_default=False))
    await tasks.delete(4)

    assert json.loads(patch.calls.last.request.content) == {"is_default": False}
    assert delete.called
