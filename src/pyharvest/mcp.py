"""MCP server for one Harvest account, over stdio.

Reads ``HARVEST_TOKEN`` and ``HARVEST_ACCOUNT``. stdout carries the protocol,
so nothing else may print there.
"""

from __future__ import annotations

import datetime as dt
import os
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Final

# Runtime imports, not TYPE_CHECKING: MCPServer resolves tool annotations to
# find the Context parameter and to build the argument schemas.
from mcp.server.mcpserver import Context, MCPServer
from mcp_types import ToolAnnotations

from pyharvest.client import Harvest
from pyharvest.models.time_entries import TimeEntry, TimeEntryCreate, TimeEntryUpdate
from pyharvest.models.user_details import ProjectAssignment
from pyharvest.models.users import User

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

USER_AGENT: Final = "pyharvest-mcp (https://github.com/Lillecarl/pyharvest)"

INSTRUCTIONS: Final = """\
Tools for one Harvest account. Writes change real data.
my_project_assignments lists the project and task IDs a time entry needs."""

READ: Final = ToolAnnotations(read_only_hint=True)
CREATE: Final = ToolAnnotations(read_only_hint=False, destructive_hint=False)
CHANGE: Final = ToolAnnotations(read_only_hint=False, destructive_hint=True)


def harvest_from_env() -> Harvest:
    return Harvest.from_env(user_agent=os.environ.get("HARVEST_USER_AGENT", USER_AGENT))


def _harvest(ctx: Context[Harvest]) -> Harvest:
    return ctx.request_context.lifespan_context


def create_server(
    connect: Callable[[], Harvest] = harvest_from_env,
) -> MCPServer[Harvest]:
    @asynccontextmanager
    async def lifespan(_: MCPServer[Harvest]) -> AsyncIterator[Harvest]:
        async with connect() as harvest:
            yield harvest

    # WARNING: at the INFO default, httpx logs every request to stderr.
    server = MCPServer(
        "pyharvest", instructions=INSTRUCTIONS, lifespan=lifespan, log_level="WARNING"
    )

    @server.tool(annotations=READ)
    async def me(ctx: Context[Harvest]) -> User:
        """The user the token belongs to."""
        return await _harvest(ctx).users.me()

    @server.tool(annotations=READ)
    async def my_project_assignments(
        ctx: Context[Harvest],
    ) -> list[ProjectAssignment]:
        """Projects the token's user is assigned to, with their tasks."""
        return [a async for a in _harvest(ctx).user_project_assignments.me()]

    @server.tool(annotations=READ)
    async def list_time_entries(
        ctx: Context[Harvest],
        from_date: dt.date | None = None,
        to_date: dt.date | None = None,
        user_id: int | None = None,
        project_id: int | None = None,
    ) -> list[TimeEntry]:
        """Time entries, newest first. Dates are inclusive spent dates."""
        entries = _harvest(ctx).time_entries.list(
            from_=from_date, to=to_date, user_id=user_id, project_id=project_id
        )
        return [e async for e in entries]

    @server.tool(annotations=READ)
    async def get_time_entry(ctx: Context[Harvest], time_entry_id: int) -> TimeEntry:
        """One time entry by its id."""
        return await _harvest(ctx).time_entries.get(time_entry_id)

    @server.tool(annotations=CREATE)
    async def create_time_entry(
        ctx: Context[Harvest], entry: TimeEntryCreate
    ) -> TimeEntry:
        """Create a time entry. Writes to the real account."""
        return await _harvest(ctx).time_entries.create(entry)

    @server.tool(annotations=CHANGE)
    async def update_time_entry(
        ctx: Context[Harvest],
        time_entry_id: int,
        changes: TimeEntryUpdate,
    ) -> TimeEntry:
        """Change a time entry. Fields left out stay as they are; null clears."""
        return await _harvest(ctx).time_entries.update(time_entry_id, changes)

    @server.tool(annotations=CHANGE)
    async def delete_time_entry(ctx: Context[Harvest], time_entry_id: int) -> str:
        """Delete a time entry. Cannot be undone."""
        await _harvest(ctx).time_entries.delete(time_entry_id)
        return f"deleted time entry {time_entry_id}"

    return server


def main() -> None:
    create_server().run("stdio")
