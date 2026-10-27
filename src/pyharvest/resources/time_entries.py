from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.time_entries import TimeEntry

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.time_entries import (
        ApprovalStatus,
        TimeEntryCreate,
        TimeEntryUpdate,
    )


class TimeEntries:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        user_id: int | None = None,
        client_id: int | None = None,
        project_id: int | None = None,
        task_id: int | None = None,
        external_reference_id: str | None = None,
        is_billed: bool | None = None,
        is_running: bool | None = None,
        approval_status: ApprovalStatus | None = None,
        updated_since: dt.datetime | None = None,
        from_: dt.date | None = None,
        to: dt.date | None = None,
    ) -> AsyncIterator[TimeEntry]:
        return self._session.paginate(
            "time_entries",
            "time_entries",
            TimeEntry,
            params={
                "user_id": user_id,
                "client_id": client_id,
                "project_id": project_id,
                "task_id": task_id,
                "external_reference_id": external_reference_id,
                "is_billed": is_billed,
                "is_running": is_running,
                "approval_status": approval_status,
                "updated_since": updated_since,
                "from": from_,
                "to": to,
            },
        )

    async def get(self, time_entry_id: int) -> TimeEntry:
        return await self._session.get(f"time_entries/{time_entry_id}", TimeEntry)

    async def create(self, entry: TimeEntryCreate) -> TimeEntry:
        return await self._session.send("POST", "time_entries", TimeEntry, entry)

    async def update(self, time_entry_id: int, changes: TimeEntryUpdate) -> TimeEntry:
        return await self._session.send(
            "PATCH", f"time_entries/{time_entry_id}", TimeEntry, changes
        )

    async def delete(self, time_entry_id: int) -> None:
        await self._session.delete(f"time_entries/{time_entry_id}")

    async def delete_external_reference(self, time_entry_id: int) -> None:
        await self._session.delete(f"time_entries/{time_entry_id}/external_reference")

    async def restart(self, time_entry_id: int) -> TimeEntry:
        return await self._session.send(
            "PATCH", f"time_entries/{time_entry_id}/restart", TimeEntry
        )

    async def stop(self, time_entry_id: int) -> TimeEntry:
        return await self._session.send(
            "PATCH", f"time_entries/{time_entry_id}/stop", TimeEntry
        )
