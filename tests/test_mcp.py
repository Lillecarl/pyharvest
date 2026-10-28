from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from mcp import Client

from pyharvest import Harvest
from pyharvest.mcp import create_server

from . import fixtures, fixtures_user_details

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    import respx

pytestmark = pytest.mark.anyio


@pytest.fixture
async def client(router: respx.MockRouter) -> AsyncIterator[Client]:
    server = create_server(
        lambda: Harvest(
            access_token="tok",
            account_id="42",
            user_agent="pyharvest-tests (ada@example.com)",
        )
    )
    async with Client(server) as client:
        yield client


async def test_lists_tools(client: Client) -> None:
    tools = {t.name: t for t in (await client.list_tools()).tools}
    assert sorted(tools) == [
        "create_time_entry",
        "delete_time_entry",
        "get_time_entry",
        "list_time_entries",
        "me",
        "my_project_assignments",
        "update_time_entry",
    ]
    assert tools["me"].annotations and tools["me"].annotations.read_only_hint


async def test_me(client: Client, router: respx.MockRouter) -> None:
    router.get("users/me").respond(json=fixtures.user())
    result = await client.call_tool("me", {})
    assert not result.is_error
    assert result.structured_content
    assert result.structured_content["id"] == fixtures.user()["id"]


async def test_my_project_assignments(client: Client, router: respx.MockRouter) -> None:
    router.get("users/me/project_assignments").respond(
        json=fixtures.page(
            "project_assignments", [fixtures_user_details.project_assignment()], None
        )
    )
    result = await client.call_tool("my_project_assignments", {})
    assert result.structured_content
    [assignment] = result.structured_content["result"]
    assert assignment["project"]["name"] == "Engine"


async def test_list_time_entries_passes_dates(
    client: Client, router: respx.MockRouter
) -> None:
    route = router.get("time_entries").respond(
        json=fixtures.page("time_entries", [fixtures.time_entry()], None)
    )
    result = await client.call_tool(
        "list_time_entries", {"from_date": "2024-03-01", "to_date": "2024-03-31"}
    )
    assert not result.is_error
    params = route.calls.last.request.url.params
    assert (params["from"], params["to"]) == ("2024-03-01", "2024-03-31")


async def test_get_time_entry(client: Client, router: respx.MockRouter) -> None:
    router.get("time_entries/7").respond(json=fixtures.time_entry(id=7))
    result = await client.call_tool("get_time_entry", {"time_entry_id": 7})
    assert result.structured_content
    assert result.structured_content["id"] == 7


async def test_update_sends_only_given_fields(
    client: Client, router: respx.MockRouter
) -> None:
    route = router.patch("time_entries/7").respond(json=fixtures.time_entry())
    result = await client.call_tool(
        "update_time_entry", {"time_entry_id": 7, "changes": {"notes": None}}
    )
    assert not result.is_error
    assert json.loads(route.calls.last.request.content) == {"notes": None}


async def test_harvest_error_is_a_tool_error(
    client: Client, router: respx.MockRouter
) -> None:
    router.delete("time_entries/7").respond(404, json={"message": "Not found"})
    result = await client.call_tool("delete_time_entry", {"time_entry_id": 7})
    assert result.is_error
