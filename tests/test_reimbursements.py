from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.reimbursements import (
    ReimbursementPayoutStatus,
    ReimbursementQueue,
)
from pyharvest.resources.reimbursements import Reimbursements

from . import fixtures, fixtures_reimbursements

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_list_renders_filters(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("reimbursements").respond(
        json=fixtures.page(
            "reimbursements", [fixtures_reimbursements.reimbursement()], None
        )
    )

    found = [
        r
        async for r in Reimbursements(harvest._session).list(
            status=ReimbursementQueue.REIMBURSED,
            project_id=3,
            from_=dt.date(2024, 3, 1),
            to=dt.date(2024, 3, 31),
        )
    ]

    assert found[0].total_cost == Decimal("33.35")
    assert found[0].payout_status is ReimbursementPayoutStatus.READY
    assert found[0].expense_category.unit_name is None
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "status": "reimbursed",
        "project_id": "3",
        "from": "2024-03-01",
        "to": "2024-03-31",
    }


@pytest.mark.anyio
async def test_reject_and_restore(harvest: Harvest, router: respx.MockRouter) -> None:
    reject = router.post("reimbursements/700/reject").respond(
        json=fixtures_reimbursements.reimbursement(
            status="rejected", rejected_reason="No receipt"
        )
    )
    restore = router.post("reimbursements/700/restore").respond(
        json=fixtures_reimbursements.reimbursement()
    )
    resource = Reimbursements(harvest._session)

    rejected = await resource.reject(700, "No receipt")
    restored = await resource.restore(700)

    assert rejected.status is ReimbursementQueue.REJECTED
    assert json.loads(reject.calls.last.request.content) == {"reason": "No receipt"}
    assert restored.rejected_reason is None
    assert restore.calls.last.request.content == b""
