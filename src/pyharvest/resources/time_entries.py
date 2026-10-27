from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest._session import body
from pyharvest.models.time_entries import TimeEntry

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator
    from decimal import Decimal

    from pyharvest._session import Session
    from pyharvest.models.time_entries import ApprovalStatus, ExternalReferenceInput


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

    async def create(
        self,
        *,
        project_id: int,
        task_id: int,
        spent_date: dt.date,
        user_id: int | None = None,
        hours: Decimal | None = None,
        started_time: str | None = None,
        ended_time: str | None = None,
        notes: str | None = None,
        external_reference: ExternalReferenceInput | None = None,
    ) -> TimeEntry:
        """Create a time entry.

        Pass ``hours`` on accounts that track duration, ``started_time`` and
        ``ended_time`` on accounts that track start and end times. Leaving
        both out starts a timer.
        """
        return await self._session.send(
            "POST",
            "time_entries",
            TimeEntry,
            json=body(
                {
                    "project_id": project_id,
                    "task_id": task_id,
                    "spent_date": spent_date,
                    "user_id": user_id,
                    "hours": hours,
                    "started_time": started_time,
                    "ended_time": ended_time,
                    "notes": notes,
                    "external_reference": external_reference,
                }
            ),
        )

    async def update(
        self,
        time_entry_id: int,
        *,
        project_id: int | None = None,
        task_id: int | None = None,
        spent_date: dt.date | None = None,
        hours: Decimal | None = None,
        started_time: str | None = None,
        ended_time: str | None = None,
        notes: str | None = None,
        external_reference: ExternalReferenceInput | None = None,
    ) -> TimeEntry:
        return await self._session.send(
            "PATCH",
            f"time_entries/{time_entry_id}",
            TimeEntry,
            json=body(
                {
                    "project_id": project_id,
                    "task_id": task_id,
                    "spent_date": spent_date,
                    "hours": hours,
                    "started_time": started_time,
                    "ended_time": ended_time,
                    "notes": notes,
                    "external_reference": external_reference,
                }
            ),
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
