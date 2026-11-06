"""Read-only checks against a real Harvest account.

Skipped unless HARVEST_TOKEN and HARVEST_ACCOUNT are set, so the Nix build
(no network) never runs them. They only GET: the account holds real data.
"""

from __future__ import annotations

import datetime as dt
import os
from typing import TYPE_CHECKING, Any

import pytest
from mcp import Client as McpClient

from pyharvest import Harvest
from pyharvest.mcp import create_server, harvest_from_env
from pyharvest.models.time_entries import TimeEntry

from . import livecheck

TODAY = livecheck.TODAY

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from pydantic import BaseModel

    from pyharvest._session import QueryValue

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.skipif(
        not (os.environ.get("HARVEST_TOKEN") and os.environ.get("HARVEST_ACCOUNT")),
        reason="needs HARVEST_TOKEN and HARVEST_ACCOUNT",
    ),
]


@pytest.fixture
async def harvest() -> AsyncIterator[Harvest]:
    async with Harvest.from_env(user_agent="pyharvest live tests") as harvest:
        yield harvest


@pytest.mark.parametrize(("path", "key", "model", "params"), livecheck.LISTS)
async def test_models_cover_live_fields(
    harvest: Harvest,
    path: str,
    key: str,
    model: type[BaseModel],
    params: dict[str, QueryValue],
) -> None:
    await livecheck.check_list(harvest, path, key, model, params)


@pytest.mark.parametrize(("path", "model"), livecheck.OBJECTS)
async def test_objects_cover_live_fields(
    harvest: Harvest, path: str, model: type[BaseModel]
) -> None:
    await livecheck.check_object(harvest, path, model)


async def test_time_entries_paginate(harvest: Harvest) -> None:
    session = harvest._session
    total = (
        await session.request("GET", "time_entries", params={"per_page": 1})
    ).json()["total_entries"]
    if total < 3:
        pytest.skip("needs three time entries to cross pages")
    # Small pages force several links.next hops over the same records.
    ids = [
        e.id
        async for e in session.paginate(
            "time_entries", "time_entries", TimeEntry, params={"per_page": 2}
        )
    ]
    assert len(ids) == total == len(set(ids))


@pytest.mark.parametrize(
    ("tool", "arguments"),
    [
        ("me", {}),
        ("my_projects", {}),
        (
            "time_summary",
            {"from_date": str(TODAY - dt.timedelta(days=30)), "to_date": str(TODAY)},
        ),
        ("list_time_entries", {"from_date": str(TODAY - dt.timedelta(days=7))}),
    ],
)
async def test_mcp_read_tools(tool: str, arguments: dict[str, Any]) -> None:
    async with McpClient(create_server(harvest_from_env)) as client:
        result = await client.call_tool(tool, arguments)
    assert not result.is_error, result.content
