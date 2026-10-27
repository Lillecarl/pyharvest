from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.approvals import ApprovalBucket, ApprovalSubmit
from pyharvest.resources.approvals import Approvals

from . import fixtures, fixtures_approvals

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_list_renders_period(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("approvals").respond(
        json=fixtures.page("approvals", [fixtures_approvals.approval()], None)
    )

    found = [
        a
        async for a in Approvals(harvest._session).list(
            dt.date(2024, 3, 4),
            dt.date(2024, 3, 10),
            approval_status=ApprovalBucket.APPROVED,
            user_id=1,
        )
    ]

    assert found[0].total_hours == Decimal("32.5")
    assert found[0].expenses_by_currency[0].billable_amount == Decimal("100.25")
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "period_start": "2024-03-04",
        "period_end": "2024-03-10",
        "approval_status": "approved",
        "user_id": "1",
    }


@pytest.mark.anyio
async def test_submit_body(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("approvals/submit").respond(
        json=fixtures_approvals.submission()
    )

    result = await Approvals(harvest._session).submit(
        ApprovalSubmit(
            period_start=dt.date(2024, 3, 4), period_end=dt.date(2024, 3, 10)
        )
    )

    assert result.period_end == dt.date(2024, 3, 10)
    assert json.loads(route.calls.last.request.content) == {
        "period_start": "2024-03-04",
        "period_end": "2024-03-10",
    }
