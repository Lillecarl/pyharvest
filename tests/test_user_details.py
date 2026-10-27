from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.user_details import TeammatesUpdate, UserRateCreate
from pyharvest.resources.user_details import (
    UserBillableRates,
    UserCostRates,
    UserProjectAssignments,
    UserTeammates,
)

from . import fixtures, fixtures_user_details

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_teammates_list(harvest: Harvest, router: respx.MockRouter) -> None:
    router.get("users/1/teammates").respond(
        json=fixtures.page("teammates", [fixtures_user_details.teammate()], None)
    )

    teammates = [t async for t in UserTeammates(harvest._session).list(1)]

    assert [t.email for t in teammates] == ["charles@example.com"]


@pytest.mark.anyio
async def test_teammates_update_sends_empty_list(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.patch("users/1/teammates").respond(json={"teammates": []})

    result = await UserTeammates(harvest._session).update(
        1, TeammatesUpdate(teammate_ids=[])
    )

    assert list(result) == []
    assert json.loads(route.calls.last.request.content) == {"teammate_ids": []}


@pytest.mark.anyio
async def test_billable_rate_create(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("users/1/billable_rates").respond(
        201, json=fixtures_user_details.rate()
    )

    created = await UserBillableRates(harvest._session).create(
        1, UserRateCreate(amount=8.25, start_date=dt.date(2024, 1, 1))
    )

    assert created.amount == Decimal("8.25")
    assert json.loads(route.calls.last.request.content) == {
        "amount": 8.25,
        "start_date": "2024-01-01",
    }


@pytest.mark.anyio
async def test_cost_rate_get_and_list(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("users/1/cost_rates/20").respond(
        json=fixtures_user_details.rate(start_date=None)
    )
    router.get("users/1/cost_rates").respond(
        json=fixtures.page("cost_rates", [fixtures_user_details.rate()], None)
    )
    rates = UserCostRates(harvest._session)

    single = await rates.get(1, 20)
    listed = [r async for r in rates.list(1)]

    assert single.start_date is None
    assert listed[0].start_date == dt.date(2024, 1, 1)


@pytest.mark.anyio
async def test_project_assignments_list_renders_filter(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.get("users/1/project_assignments").respond(
        json=fixtures.page(
            "project_assignments", [fixtures_user_details.project_assignment()], None
        )
    )

    assignments = [
        a
        async for a in UserProjectAssignments(harvest._session).list(
            1, updated_since=dt.datetime(2024, 3, 1, tzinfo=dt.UTC)
        )
    ]

    assert assignments[0].task_assignments[0].budget == Decimal("12.5")
    assert assignments[0].client.currency == "EUR"
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "updated_since": "2024-03-01T00:00:00Z",
    }


@pytest.mark.anyio
async def test_project_assignments_me(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.get("users/me/project_assignments").respond(
        json=fixtures.page(
            "project_assignments", [fixtures_user_details.project_assignment()], None
        )
    )

    assignments = [a async for a in UserProjectAssignments(harvest._session).me()]

    assert assignments[0].project.is_billable is True
    assert route.called
