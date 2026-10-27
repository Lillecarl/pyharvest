from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.imports import ImportStatus, ImportType
from pyharvest.resources.imports import Imports

from . import fixtures, fixtures_imports

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_list_renders_filters(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("imports").respond(
        json=fixtures.page("imports", [fixtures_imports.import_run()], None)
    )

    found = [
        i
        async for i in Imports(harvest._session).list(
            updated_since=dt.datetime(2024, 3, 1, tzinfo=dt.UTC)
        )
    ]

    assert found[0].import_type is ImportType.PROJECT
    assert found[0].reverted_at is None
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "updated_since": "2024-03-01T00:00:00Z",
    }


@pytest.mark.anyio
async def test_get_and_revert(harvest: Harvest, router: respx.MockRouter) -> None:
    router.get("imports/600").respond(json=fixtures_imports.import_run())
    revert = router.post("imports/600/revert").respond(
        json=fixtures_imports.import_run(status="reverting")
    )
    resource = Imports(harvest._session)

    assert (await resource.get(600)).id == 600
    assert (await resource.revert(600)).status is ImportStatus.REVERTING
    assert revert.calls.last.request.content == b""


@pytest.mark.anyio
async def test_csv_errors_returns_text(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    body = "Client,Project\n,Website Redesign\n"
    router.get("imports/600/csv_errors").respond(
        text=body, headers={"Content-Type": "text/csv"}
    )

    assert await Imports(harvest._session).csv_errors(600) == body
