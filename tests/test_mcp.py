from __future__ import annotations

import datetime as dt
import json
from typing import TYPE_CHECKING

import httpx
import pytest
from mcp import Client

from pyharvest import Harvest
from pyharvest.mcp import create_server, summarise
from pyharvest.models.time_entries import TimeEntry

from . import fixtures, fixtures_company, fixtures_expenses, fixtures_user_details

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from pathlib import Path

    import respx


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


def entry(**overrides: object) -> TimeEntry:
    return TimeEntry.model_validate(fixtures.time_entry(**overrides))


def test_summarise_lists_empty_days_and_sums_exactly() -> None:
    summary = summarise(
        [
            entry(spent_date="2024-03-01", hours=0.1),
            entry(spent_date="2024-03-01", hours=0.2),
            entry(spent_date="2024-03-03", hours=1, task={"id": 9, "name": "Docs"}),
        ],
        dt.date(2024, 3, 1),
        dt.date(2024, 3, 4),
        daily_target_hours=0.3,
    )
    assert list(summary.days.values()) == [0.3, 0.0, 1.0, 0.0]
    # Fri meets the 0.3 target exactly; Sat and Sun are not weekdays.
    assert summary.short_weekdays == [dt.date(2024, 3, 4)]
    assert summary.total_hours == 1.3
    assert [(t.task, t.hours) for t in summary.tasks] == [
        ("Docs", 1.0),
        ("Programming", 0.3),
    ]


@pytest.mark.anyio
async def test_lists_tools(client: Client) -> None:
    tools = {t.name: t for t in (await client.list_tools()).tools}
    assert sorted(tools) == [
        "create_expense",
        "create_time_entries",
        "delete_expense",
        "delete_time_entry",
        "download_receipt",
        "expense_categories",
        "get_time_entry",
        "harvest_get",
        "list_expenses",
        "list_time_entries",
        "me",
        "my_projects",
        "restart_timer",
        "running_timer",
        "stop_timer",
        "time_summary",
        "update_expense",
        "update_time_entry",
    ]
    assert tools["me"].annotations and tools["me"].annotations.read_only_hint
    me_schema = tools["me"].output_schema or {}
    assert "description" in me_schema["properties"]["wants_timestamp_timers"]


@pytest.mark.anyio
async def test_me_joins_user_and_company(
    client: Client, router: respx.MockRouter
) -> None:
    router.get("users/me").respond(json=fixtures.user())
    router.get("company").respond(json=fixtures_company.company())
    result = await client.call_tool("me", {})
    assert result.structured_content == {
        "id": fixtures.user()["id"],
        "name": "Ada Lovelace",
        "email": fixtures.user()["email"],
        "timezone": "Europe/Stockholm",
        "weekly_capacity_hours": 40.0,
        "access_roles": fixtures.user()["access_roles"],
        "company": "ABC Corp",
        "week_start_day": "Monday",
        "clock": "24h",
        "wants_timestamp_timers": False,
        "notes_required": False,
    }


@pytest.mark.anyio
async def test_my_projects_drops_inactive(
    client: Client, router: respx.MockRouter
) -> None:
    active = fixtures_user_details.project_assignment()
    inactive = fixtures_user_details.project_assignment(id=31, is_active=False)
    router.get("users/me/project_assignments").respond(
        json=fixtures.page("project_assignments", [active, inactive], None)
    )
    result = await client.call_tool("my_projects", {"recent_days": 0})
    assert result.structured_content == {
        "result": [
            {
                "id": 3,
                "name": "Engine",
                "code": None,
                "client": "ABC Corp",
                # Unused: last_used and recent_hours are left out.
                "tasks": [{"id": 4, "name": "Programming", "billable": True}],
            }
        ]
    }


@pytest.mark.anyio
async def test_my_projects_puts_recent_use_first(
    client: Client, router: respx.MockRouter
) -> None:
    unused = fixtures_user_details.project_assignment()
    used = fixtures_user_details.project_assignment(
        id=31, project={"id": 8, "name": "Docs", "code": None, "is_billable": True}
    )
    router.get("users/me/project_assignments").respond(
        json=fixtures.page("project_assignments", [unused, used], None)
    )
    router.get("users/me").respond(json=fixtures.user())
    route = router.get("time_entries").respond(
        json=fixtures.page(
            "time_entries",
            [
                fixtures.time_entry(
                    spent_date="2024-03-02",
                    hours=0.1,
                    project={"id": 8, "name": "Docs"},
                ),
                fixtures.time_entry(
                    spent_date="2024-03-05",
                    hours=0.2,
                    project={"id": 8, "name": "Docs"},
                ),
            ],
            None,
        )
    )
    result = await client.call_tool("my_projects", {})
    assert route.calls.last.request.url.params["user_id"] == str(fixtures.user()["id"])
    assert result.structured_content
    first, second = result.structured_content["result"]
    assert (first["id"], second["id"]) == (8, 3)
    assert first["tasks"][0]["last_used"] == "2024-03-05"
    assert first["tasks"][0]["recent_hours"] == 0.3


@pytest.mark.anyio
async def test_list_time_entries_returns_rows(
    client: Client, router: respx.MockRouter
) -> None:
    route = router.get("time_entries").respond(
        json=fixtures.page("time_entries", [fixtures.time_entry()], None)
    )
    result = await client.call_tool(
        "list_time_entries", {"from_date": "2024-03-01", "to_date": "2024-03-31"}
    )
    params = route.calls.last.request.url.params
    assert (params["from"], params["to"]) == ("2024-03-01", "2024-03-31")
    assert result.structured_content
    [row] = result.structured_content["result"]
    assert row["hours"] == 2.11
    assert row["project"] == "Engine"
    assert "user_assignment" not in row


@pytest.mark.anyio
async def test_time_summary_rejects_reversed_range(client: Client) -> None:
    result = await client.call_tool(
        "time_summary", {"from_date": "2024-03-02", "to_date": "2024-03-01"}
    )
    assert result.is_error
    assert "before" in str(result.content)


@pytest.mark.anyio
async def test_create_time_entries_stops_at_first_failure(
    client: Client, router: respx.MockRouter
) -> None:
    route = router.post("time_entries").mock(
        side_effect=[
            httpx.Response(201, json=fixtures.time_entry(id=1)),
            httpx.Response(422, json={"message": "Spent date is locked"}),
        ]
    )
    new = {"project_id": 3, "task_id": 4, "spent_date": "2024-03-01", "hours": 8}
    result = await client.call_tool("create_time_entries", {"entries": [new, new, new]})
    assert result.structured_content
    assert [r["id"] for r in result.structured_content["created"]] == [1]
    assert result.structured_content["failed_index"] == 1
    assert "Spent date is locked" in result.structured_content["error"]
    assert route.call_count == 2


NEW_EXPENSE = {
    "project_id": 3,
    "expense_category_id": 7,
    "spent_date": "2024-03-01",
    "total_cost": 33.35,
}


@pytest.mark.anyio
async def test_create_expense_uploads_receipt(
    client: Client, router: respx.MockRouter, tmp_path: Path
) -> None:
    route = router.post("expenses").respond(201, json=fixtures_expenses.expense())
    receipt = tmp_path / "ticket.pdf"
    receipt.write_bytes(b"%PDF-1.4")
    result = await client.call_tool(
        "create_expense", {"expense": NEW_EXPENSE, "receipt_path": str(receipt)}
    )
    assert result.structured_content
    assert result.structured_content["receipt"] == "ticket.pdf"
    assert "units" not in result.structured_content
    request = route.calls.last.request
    assert request.headers["Content-Type"].startswith("multipart/form-data")
    assert b'filename="ticket.pdf"' in request.content


@pytest.mark.anyio
async def test_create_expense_without_receipt_sends_json(
    client: Client, router: respx.MockRouter
) -> None:
    route = router.post("expenses").respond(201, json=fixtures_expenses.expense())
    result = await client.call_tool("create_expense", {"expense": NEW_EXPENSE})
    assert not result.is_error
    assert json.loads(route.calls.last.request.content) == NEW_EXPENSE


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("receipt_path", "message"),
    [("ticket.pdf", "absolute"), ("/nonexistent/ticket.pdf", "cannot read")],
)
async def test_create_expense_rejects_bad_receipt_path(
    client: Client, receipt_path: str, message: str
) -> None:
    result = await client.call_tool(
        "create_expense", {"expense": NEW_EXPENSE, "receipt_path": receipt_path}
    )
    assert result.is_error
    assert message in str(result.content)


@pytest.mark.anyio
async def test_update_expense_null_with_receipt_is_reported(
    client: Client, router: respx.MockRouter, tmp_path: Path
) -> None:
    route = router.patch("expenses/500").respond(json=fixtures_expenses.expense())
    receipt = tmp_path / "ticket.pdf"
    receipt.write_bytes(b"%PDF-1.4")
    result = await client.call_tool(
        "update_expense",
        {"expense_id": 500, "changes": {"notes": None}, "receipt_path": str(receipt)},
    )
    assert result.is_error
    assert "null" in str(result.content)
    assert not route.called


RECEIPT_URL = "https://acme.harvestapp.com/expenses/500/receipt.pdf"


def mock_receipt(router: respx.MockRouter) -> None:
    receipt = {
        "url": RECEIPT_URL,
        "file_name": "ticket.pdf",
        "file_size": 8,
        "content_type": "application/pdf",
    }
    router.get("expenses/500").respond(json=fixtures_expenses.expense(receipt=receipt))
    router.get(RECEIPT_URL).respond(content=b"%PDF-1.4")


@pytest.mark.anyio
async def test_download_receipt_into_directory(
    client: Client, router: respx.MockRouter, tmp_path: Path
) -> None:
    mock_receipt(router)
    result = await client.call_tool(
        "download_receipt", {"expense_id": 500, "path": str(tmp_path)}
    )
    assert result.structured_content
    assert result.structured_content["path"] == str(tmp_path / "ticket.pdf")
    assert (tmp_path / "ticket.pdf").read_bytes() == b"%PDF-1.4"


@pytest.mark.anyio
async def test_download_receipt_never_overwrites(
    client: Client, router: respx.MockRouter, tmp_path: Path
) -> None:
    mock_receipt(router)
    existing = tmp_path / "mine.pdf"
    existing.write_bytes(b"keep")
    result = await client.call_tool(
        "download_receipt", {"expense_id": 500, "path": str(existing)}
    )
    assert result.is_error
    assert "cannot write" in str(result.content)
    assert existing.read_bytes() == b"keep"


@pytest.mark.anyio
async def test_download_receipt_without_receipt(
    client: Client, router: respx.MockRouter, tmp_path: Path
) -> None:
    router.get("expenses/500").respond(json=fixtures_expenses.expense(receipt=None))
    result = await client.call_tool(
        "download_receipt", {"expense_id": 500, "path": str(tmp_path)}
    )
    assert result.is_error
    assert "no receipt" in str(result.content)


@pytest.mark.anyio
async def test_expense_categories(client: Client, router: respx.MockRouter) -> None:
    route = router.get("expense_categories").respond(
        json=fixtures.page(
            "expense_categories", [fixtures_expenses.expense_category()], None
        )
    )
    result = await client.call_tool("expense_categories", {})
    assert route.calls.last.request.url.params["is_active"] == "true"
    assert result.structured_content
    [row] = result.structured_content["result"]
    assert row["unit_name"] == "mile"


@pytest.mark.anyio
async def test_get_time_entry_is_full(client: Client, router: respx.MockRouter) -> None:
    router.get("time_entries/7").respond(json=fixtures.time_entry(id=7))
    result = await client.call_tool("get_time_entry", {"time_entry_id": 7})
    assert result.structured_content
    assert result.structured_content["user_assignment"]["id"] == 5


@pytest.mark.anyio
async def test_update_sends_only_given_fields(
    client: Client, router: respx.MockRouter
) -> None:
    route = router.patch("time_entries/7").respond(json=fixtures.time_entry())
    result = await client.call_tool(
        "update_time_entry", {"time_entry_id": 7, "changes": {"notes": None}}
    )
    assert not result.is_error
    assert json.loads(route.calls.last.request.content) == {"notes": None}


@pytest.mark.anyio
async def test_running_timer(client: Client, router: respx.MockRouter) -> None:
    route = router.get("time_entries").respond(
        json=fixtures.page("time_entries", [fixtures.time_entry(is_running=True)], None)
    )
    result = await client.call_tool("running_timer", {})
    assert route.calls.last.request.url.params["is_running"] == "true"
    assert result.structured_content
    assert result.structured_content["result"]["is_running"] is True


@pytest.mark.anyio
async def test_no_running_timer(client: Client, router: respx.MockRouter) -> None:
    router.get("time_entries").respond(json=fixtures.page("time_entries", [], None))
    result = await client.call_tool("running_timer", {})
    assert not result.is_error
    assert result.structured_content == {"result": None}


@pytest.mark.anyio
async def test_stop_timer(client: Client, router: respx.MockRouter) -> None:
    router.patch("time_entries/7/stop").respond(json=fixtures.time_entry(id=7))
    result = await client.call_tool("stop_timer", {"time_entry_id": 7})
    assert result.structured_content
    assert result.structured_content["id"] == 7


@pytest.mark.anyio
async def test_harvest_error_message_reaches_the_model(
    client: Client, router: respx.MockRouter
) -> None:
    router.delete("time_entries/7").respond(404, json={"message": "Not found"})
    result = await client.call_tool("delete_time_entry", {"time_entry_id": 7})
    assert result.is_error
    assert "404: Not found" in str(result.content)


@pytest.mark.anyio
async def test_harvest_get_passes_params(
    client: Client, router: respx.MockRouter
) -> None:
    route = router.get("projects/3").respond(json={"id": 3})
    result = await client.call_tool(
        "harvest_get", {"path": "projects/3", "params": {"page": 2}}
    )
    assert result.structured_content == {"id": 3}
    assert route.calls.last.request.url.params["page"] == "2"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "path",
    ["https://example.com/x", "//example.com/x", "/projects", "projects/../x", "a?b=1"],
)
async def test_harvest_get_refuses_other_hosts(
    client: Client, router: respx.MockRouter, path: str
) -> None:
    result = await client.call_tool("harvest_get", {"path": path})
    assert result.is_error
    assert not router.calls
