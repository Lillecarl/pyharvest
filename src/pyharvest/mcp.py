"""MCP server for one Harvest account, over stdio.

Reads ``HARVEST_TOKEN`` and ``HARVEST_ACCOUNT``. stdout carries the protocol,
so nothing else may print there.

Results are compact on purpose: every byte a tool returns lands in the
calling model's context. ``get_time_entry`` and ``harvest_get`` give the
full records.
"""

from __future__ import annotations

import datetime as dt
import os
import re
from collections import defaultdict
from contextlib import asynccontextmanager, contextmanager
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Final

# Runtime imports, not TYPE_CHECKING: MCPServer resolves tool annotations to
# find the Context parameter and to build the argument schemas.
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import ToolAnnotations
from pydantic import BaseModel, ConfigDict

from pyharvest.client import Harvest
from pyharvest.errors import HarvestError
from pyharvest.models.company import Company
from pyharvest.models.time_entries import TimeEntry, TimeEntryCreate, TimeEntryUpdate
from pyharvest.models.user_details import ProjectAssignment
from pyharvest.models.users import User

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable, Iterable, Iterator

USER_AGENT: Final = "pyharvest-mcp (https://github.com/Lillecarl/pyharvest)"

INSTRUCTIONS: Final = """\
Tools for one Harvest account. Writes change real data.
Start with me (user, timezone, clock, whether the account tracks durations
or start/end times) and my_projects (project and task ids for new entries).
time_summary finds days with missing hours. harvest_get reads anything else."""

READ: Final = ToolAnnotations(read_only_hint=True)
CREATE: Final = ToolAnnotations(read_only_hint=False, destructive_hint=False)
CHANGE: Final = ToolAnnotations(read_only_hint=False, destructive_hint=True)

# Letters, digits and underscores between slashes: no scheme, host, "..",
# or query, so a path can never send the token to another host.
API_PATH: Final = re.compile(r"[a-z0-9_]+(?:/[a-z0-9_]+)*")


class Result(BaseModel):
    # Field docstrings become schema descriptions the calling model reads.
    model_config = ConfigDict(use_attribute_docstrings=True)


class Me(Result):
    id: int
    name: str
    email: str
    timezone: str
    weekly_capacity_hours: float
    access_roles: list[str]
    company: str
    week_start_day: str
    clock: str
    wants_timestamp_timers: bool
    """True: entries carry started_time/ended_time. False: entries carry hours."""
    notes_required: bool


class AssignedTask(Result):
    id: int
    name: str
    billable: bool


class AssignedProject(Result):
    id: int
    name: str
    code: str | None
    client: str
    tasks: list[AssignedTask]


class EntryRow(Result):
    id: int
    spent_date: dt.date
    client: str
    project_id: int
    project: str
    task_id: int
    task: str
    hours: float
    notes: str | None
    approval_status: str
    is_running: bool
    is_locked: bool


class TaskTotal(Result):
    project_id: int
    project: str
    task_id: int
    task: str
    hours: float


class TimeSummary(Result):
    total_hours: float
    days: dict[dt.date, float]
    """Hours on each date in the range, 0 included."""
    short_weekdays: list[dt.date]
    """Monday to Friday dates under daily_target_hours. Holidays show here too."""
    tasks: list[TaskTotal]


class CreateResult(Result):
    created: list[EntryRow]
    error: str | None = None
    """Why entry number failed_index failed; entries after it were not sent."""
    failed_index: int | None = None


def to_me(user: User, company: Company) -> Me:
    return Me(
        id=user.id,
        name=f"{user.first_name} {user.last_name}",
        email=user.email,
        timezone=user.timezone,
        weekly_capacity_hours=user.weekly_capacity / 3600,
        access_roles=list(user.access_roles),
        company=company.name,
        week_start_day=company.week_start_day,
        clock=company.clock,
        wants_timestamp_timers=company.wants_timestamp_timers,
        notes_required=bool(company.day_entry_notes_required),
    )


def to_project(assignment: ProjectAssignment) -> AssignedProject:
    return AssignedProject(
        id=assignment.project.id,
        name=assignment.project.name,
        code=assignment.project.code,
        client=assignment.client.name,
        tasks=[
            AssignedTask(id=t.task.id, name=t.task.name, billable=t.billable)
            for t in assignment.task_assignments
            if t.is_active
        ],
    )


def to_row(entry: TimeEntry) -> EntryRow:
    return EntryRow(
        id=entry.id,
        spent_date=entry.spent_date,
        client=entry.client.name,
        project_id=entry.project.id,
        project=entry.project.name,
        task_id=entry.task.id,
        task=entry.task.name,
        hours=float(entry.hours),
        notes=entry.notes,
        approval_status=entry.approval_status,
        is_running=entry.is_running,
        is_locked=entry.is_locked,
    )


def summarise(
    entries: Iterable[TimeEntry],
    from_date: dt.date,
    to_date: dt.date,
    daily_target_hours: float,
) -> TimeSummary:
    # Decimal sums: float addition turns 0.1 + 0.2 into 0.30000000000000004.
    by_day: defaultdict[dt.date, Decimal] = defaultdict(Decimal)
    by_task: defaultdict[tuple[int, str, int, str], Decimal] = defaultdict(Decimal)
    for e in entries:
        by_day[e.spent_date] += e.hours
        by_task[(e.project.id, e.project.name, e.task.id, e.task.name)] += e.hours
    span = (to_date - from_date).days + 1
    days = [from_date + dt.timedelta(days=n) for n in range(span)]
    return TimeSummary(
        total_hours=float(sum(by_day.values(), Decimal())),
        days={d: float(by_day[d]) for d in days},
        short_weekdays=[
            d
            for d in days
            if d.weekday() < 5 and by_day[d] < Decimal(str(daily_target_hours))
        ],
        tasks=[
            TaskTotal(
                project_id=pid, project=project, task_id=tid, task=task, hours=float(h)
            )
            for (pid, project, tid, task), h in sorted(
                by_task.items(), key=lambda item: -item[1]
            )
        ],
    )


@contextmanager
def reported() -> Iterator[None]:
    """Show Harvest's message to the model.

    MCPServer replaces the text of any exception but ToolError with a bare
    "Error executing tool <name>".
    """
    try:
        yield
    except HarvestError as exc:
        raise ToolError(str(exc)) from exc


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
    async def me(ctx: Context[Harvest]) -> Me:
        """The token's user and the account settings that shape a time entry."""
        harvest = _harvest(ctx)
        with reported():
            return to_me(await harvest.users.me(), await harvest.company.get())

    @server.tool(annotations=READ)
    async def my_projects(ctx: Context[Harvest]) -> list[AssignedProject]:
        """Active projects the token's user may log time to, with active tasks."""
        with reported():
            return [
                to_project(a)
                async for a in _harvest(ctx).user_project_assignments.me()
                if a.is_active
            ]

    @server.tool(annotations=READ)
    async def list_time_entries(
        ctx: Context[Harvest],
        from_date: dt.date | None = None,
        to_date: dt.date | None = None,
        user_id: int | None = None,
        project_id: int | None = None,
    ) -> list[EntryRow]:
        """Time entries as compact rows, newest first.

        Dates are inclusive spent dates. Without user_id, an admin sees
        everyone's entries. get_time_entry has the full record.
        """
        entries = _harvest(ctx).time_entries.list(
            from_=from_date, to=to_date, user_id=user_id, project_id=project_id
        )
        with reported():
            return [to_row(e) async for e in entries]

    @server.tool(annotations=READ)
    async def time_summary(
        ctx: Context[Harvest],
        from_date: dt.date,
        to_date: dt.date,
        user_id: int | None = None,
        daily_target_hours: float = 8.0,
    ) -> TimeSummary:
        """Hours per date and per project task over an inclusive date range.

        short_weekdays lists the weekdays under daily_target_hours: where time
        is missing.
        """
        if to_date < from_date:
            raise ToolError("to_date is before from_date")
        entries = _harvest(ctx).time_entries.list(
            from_=from_date, to=to_date, user_id=user_id
        )
        with reported():
            return summarise(
                [e async for e in entries], from_date, to_date, daily_target_hours
            )

    @server.tool(annotations=READ)
    async def get_time_entry(ctx: Context[Harvest], time_entry_id: int) -> TimeEntry:
        """One time entry with every field Harvest returns."""
        with reported():
            return await _harvest(ctx).time_entries.get(time_entry_id)

    @server.tool(annotations=CREATE)
    async def create_time_entries(
        ctx: Context[Harvest], entries: list[TimeEntryCreate]
    ) -> CreateResult:
        """Create time entries, in order. Writes to the real account.

        Give hours on a duration account, started_time/ended_time on a
        timestamp one (see me). With neither, Harvest starts a timer on the
        new entry and stops the user's running one. Stops at the first
        failure and reports it; the entries created before it stay.
        """
        harvest = _harvest(ctx)
        created: list[EntryRow] = []
        for index, entry in enumerate(entries):
            try:
                created.append(to_row(await harvest.time_entries.create(entry)))
            except HarvestError as exc:
                return CreateResult(created=created, error=str(exc), failed_index=index)
        return CreateResult(created=created)

    @server.tool(annotations=CHANGE)
    async def update_time_entry(
        ctx: Context[Harvest],
        time_entry_id: int,
        changes: TimeEntryUpdate,
    ) -> EntryRow:
        """Change a time entry. Fields left out stay as they are; null clears."""
        with reported():
            return to_row(
                await _harvest(ctx).time_entries.update(time_entry_id, changes)
            )

    @server.tool(annotations=CHANGE)
    async def delete_time_entry(ctx: Context[Harvest], time_entry_id: int) -> str:
        """Delete a time entry. Cannot be undone."""
        with reported():
            await _harvest(ctx).time_entries.delete(time_entry_id)
        return f"deleted time entry {time_entry_id}"

    @server.tool(annotations=READ)
    async def running_timer(
        ctx: Context[Harvest], user_id: int | None = None
    ) -> EntryRow | None:
        """The time entry whose timer runs now, or null.

        Starting a timer stops the running one, so a user has at most one.
        Without user_id, an admin may get someone else's.
        """
        entries = _harvest(ctx).time_entries.list(is_running=True, user_id=user_id)
        with reported():
            async for e in entries:
                return to_row(e)
        return None

    @server.tool(annotations=CHANGE)
    async def stop_timer(ctx: Context[Harvest], time_entry_id: int) -> EntryRow:
        """Stop the running timer on a time entry."""
        with reported():
            return to_row(await _harvest(ctx).time_entries.stop(time_entry_id))

    @server.tool(annotations=CHANGE)
    async def restart_timer(ctx: Context[Harvest], time_entry_id: int) -> EntryRow:
        """Start the timer again on a stopped time entry."""
        with reported():
            return to_row(await _harvest(ctx).time_entries.restart(time_entry_id))

    @server.tool(annotations=READ)
    async def harvest_get(
        ctx: Context[Harvest],
        path: str,
        params: dict[str, str | int | bool] | None = None,
    ) -> dict[str, Any]:
        """GET any Harvest API v2 path, raw JSON, one page.

        path is relative to /v2/, for example "projects/123",
        "reports/time/projects" or "users/me/project_assignments". params are
        the query parameters the API docs list (dates as YYYY-MM-DD). For more
        pages, pass page=next_page from the result. A member gets 403 on most
        admin sections.
        """
        if not API_PATH.fullmatch(path):
            raise ToolError(f"not an API path: {path!r}")
        with reported():
            response = await _harvest(ctx)._session.request("GET", path, params=params)
        # Any: the raw JSON of whichever endpoint was asked for.
        return response.json()

    return server


def main() -> None:
    create_server().run("stdio")
