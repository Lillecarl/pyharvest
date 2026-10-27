from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.pto import (
    HolidayCalendar,
    HolidayCalendarEntry,
    PtoAllocation,
    PtoAllocationBulkResult,
    PtoAllocationBulkUpdate,
    PtoAllocationOutcome,
    PtoAssignment,
    TimeOffBalanceSheet,
    TimeOffBulkResult,
    TimeOffBulkReview,
    TimeOffPolicy,
    TimeOffRequest,
    TimeOffReview,
    WorkSchedule,
)

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator, Sequence

    from pyharvest._session import Session
    from pyharvest.models.pto import (
        HolidayCalendarCreate,
        HolidayCalendarEntryCreate,
        HolidayCalendarEntryUpdate,
        HolidayCalendarUpdate,
        PtoAllocationBulkItem,
        PtoAllocationReset,
        PtoAllocationUpdate,
        PtoAssignmentUpdate,
        TimeOffPolicyCreate,
        TimeOffPolicyUpdate,
        TimeOffRequestCreate,
        TimeOffRequestStatus,
        TimeOffRequestUpdate,
        WorkScheduleCreate,
        WorkScheduleUpdate,
    )


def _id_list(ids: Sequence[int] | None) -> str | None:
    # Comma-joined: unverified against a PTO-enabled account.
    return None if ids is None else ",".join(map(str, ids))


class WorkSchedules:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self, *, is_active: bool | None = None) -> AsyncIterator[WorkSchedule]:
        return self._session.paginate(
            "pto/work_schedules",
            "pto_work_schedules",
            WorkSchedule,
            params={"is_active": is_active},
        )

    async def get(self, work_schedule_id: int) -> WorkSchedule:
        return await self._session.get(
            f"pto/work_schedules/{work_schedule_id}", WorkSchedule
        )

    async def create(self, schedule: WorkScheduleCreate) -> WorkSchedule:
        return await self._session.send(
            "POST", "pto/work_schedules", WorkSchedule, schedule
        )

    async def update(
        self, work_schedule_id: int, changes: WorkScheduleUpdate
    ) -> WorkSchedule:
        return await self._session.send(
            "PATCH", f"pto/work_schedules/{work_schedule_id}", WorkSchedule, changes
        )

    async def deactivate(self, work_schedule_id: int) -> WorkSchedule:
        """DELETE deactivates; the default schedule cannot be deactivated."""
        return await self._session.send(
            "DELETE", f"pto/work_schedules/{work_schedule_id}", WorkSchedule
        )


class TimeOffRequests:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        user_id: int | None = None,
        status: TimeOffRequestStatus | None = None,
        pto_type_id: int | None = None,
        from_: dt.date | None = None,
        to: dt.date | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[TimeOffRequest]:
        return self._session.paginate(
            "pto/requests",
            "pto_requests",
            TimeOffRequest,
            params={
                "user_id": user_id,
                "status": status,
                "pto_type_id": pto_type_id,
                "from": from_,
                "to": to,
                "updated_since": updated_since,
            },
        )

    async def get(self, request_id: int) -> TimeOffRequest:
        return await self._session.get(f"pto/requests/{request_id}", TimeOffRequest)

    async def create(self, request: TimeOffRequestCreate) -> TimeOffRequest:
        return await self._session.send("POST", "pto/requests", TimeOffRequest, request)

    async def update(
        self, request_id: int, changes: TimeOffRequestUpdate
    ) -> TimeOffRequest:
        """Harvest cancels the original and returns a replacement with a new id."""
        return await self._session.send(
            "PATCH", f"pto/requests/{request_id}", TimeOffRequest, changes
        )

    async def cancel(self, request_id: int) -> TimeOffRequest:
        """DELETE cancels; the request stays listed with status cancelled."""
        return await self._session.send(
            "DELETE", f"pto/requests/{request_id}", TimeOffRequest
        )

    async def approve(self, request_id: int) -> TimeOffRequest:
        return await self._session.send(
            "POST", f"pto/requests/{request_id}/approve", TimeOffRequest
        )

    async def decline(
        self, request_id: int, reason: str | None = None
    ) -> TimeOffRequest:
        return await self._session.send(
            "POST",
            f"pto/requests/{request_id}/decline",
            TimeOffRequest,
            None if reason is None else TimeOffReview(reason=reason),
        )

    async def request_changes(self, request_id: int, reason: str) -> TimeOffRequest:
        return await self._session.send(
            "POST",
            f"pto/requests/{request_id}/request_changes",
            TimeOffRequest,
            TimeOffReview(reason=reason),
        )

    async def approve_many(self, request_ids: Sequence[int]) -> TimeOffBulkResult:
        """Up to 2000 ids. Requests not pending come back in ``skipped_ids``."""
        return await self._session.send(
            "POST",
            "pto/requests/approve",
            TimeOffBulkResult,
            TimeOffBulkReview(ids=list(request_ids)),
        )

    async def decline_many(
        self, request_ids: Sequence[int], reason: str | None = None
    ) -> TimeOffBulkResult:
        body = (
            TimeOffBulkReview(ids=list(request_ids))
            if reason is None
            else TimeOffBulkReview(ids=list(request_ids), reason=reason)
        )
        return await self._session.send(
            "POST", "pto/requests/decline", TimeOffBulkResult, body
        )


class TimeOffPolicies:
    """Harvest's ``pto/types``."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        is_active: bool | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[TimeOffPolicy]:
        return self._session.paginate(
            "pto/types",
            "pto_types",
            TimeOffPolicy,
            params={"is_active": is_active, "updated_since": updated_since},
        )

    async def get(self, policy_id: int) -> TimeOffPolicy:
        return await self._session.get(f"pto/types/{policy_id}", TimeOffPolicy)

    async def create(self, policy: TimeOffPolicyCreate) -> TimeOffPolicy:
        return await self._session.send("POST", "pto/types", TimeOffPolicy, policy)

    async def update(
        self, policy_id: int, changes: TimeOffPolicyUpdate
    ) -> TimeOffPolicy:
        return await self._session.send(
            "PATCH", f"pto/types/{policy_id}", TimeOffPolicy, changes
        )

    async def deactivate(self, policy_id: int) -> TimeOffPolicy:
        """DELETE without parameters deactivates and keeps the history."""
        return await self._session.send(
            "DELETE", f"pto/types/{policy_id}", TimeOffPolicy
        )

    async def delete_with_history(self, policy_id: int) -> None:
        """Delete the policy and every request booked against it."""
        await self._session.request(
            "DELETE",
            f"pto/types/{policy_id}",
            params={"keep_history": False, "confirm_delete_history": 1},
        )


class TimeOffBalances:
    def __init__(self, session: Session) -> None:
        self._session = session

    async def get(
        self,
        *,
        user_id: int | None = None,
        year: int | None = None,
        as_of: dt.date | None = None,
    ) -> TimeOffBalanceSheet:
        """Defaults: the authenticated user, this year, today."""
        return await self._session.get(
            "pto/balances",
            TimeOffBalanceSheet,
            params={"user_id": user_id, "year": year, "as_of": as_of},
        )


class HolidayCalendars:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> AsyncIterator[HolidayCalendar]:
        return self._session.paginate(
            "pto/holiday_calendars", "pto_holiday_calendars", HolidayCalendar
        )

    async def get(self, calendar_id: int) -> HolidayCalendar:
        return await self._session.get(
            f"pto/holiday_calendars/{calendar_id}", HolidayCalendar
        )

    async def create(self, calendar: HolidayCalendarCreate) -> HolidayCalendar:
        return await self._session.send(
            "POST", "pto/holiday_calendars", HolidayCalendar, calendar
        )

    async def update(
        self, calendar_id: int, changes: HolidayCalendarUpdate
    ) -> HolidayCalendar:
        return await self._session.send(
            "PATCH", f"pto/holiday_calendars/{calendar_id}", HolidayCalendar, changes
        )

    async def delete(self, calendar_id: int) -> HolidayCalendar:
        return await self._session.send(
            "DELETE", f"pto/holiday_calendars/{calendar_id}", HolidayCalendar
        )


class HolidayCalendarEntries:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self, calendar_id: int) -> AsyncIterator[HolidayCalendarEntry]:
        return self._session.paginate(
            f"pto/holiday_calendars/{calendar_id}/entries",
            "pto_holiday_calendar_entries",
            HolidayCalendarEntry,
        )

    async def create(
        self, calendar_id: int, entry: HolidayCalendarEntryCreate
    ) -> HolidayCalendarEntry:
        return await self._session.send(
            "POST",
            f"pto/holiday_calendars/{calendar_id}/entries",
            HolidayCalendarEntry,
            entry,
        )

    async def update(
        self, calendar_id: int, entry_id: int, changes: HolidayCalendarEntryUpdate
    ) -> HolidayCalendarEntry:
        return await self._session.send(
            "PATCH",
            f"pto/holiday_calendars/{calendar_id}/entries/{entry_id}",
            HolidayCalendarEntry,
            changes,
        )

    async def delete(self, calendar_id: int, entry_id: int) -> HolidayCalendarEntry:
        return await self._session.send(
            "DELETE",
            f"pto/holiday_calendars/{calendar_id}/entries/{entry_id}",
            HolidayCalendarEntry,
        )


class PtoAssignments:
    """Each user's holiday calendar and work schedule."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        user_id: int | None = None,
        user_ids: Sequence[int] | None = None,
    ) -> AsyncIterator[PtoAssignment]:
        return self._session.paginate(
            "pto/assignments",
            "assignments",
            PtoAssignment,
            params={"user_id": user_id, "user_ids": _id_list(user_ids)},
        )

    async def update(self, user_id: int, changes: PtoAssignmentUpdate) -> PtoAssignment:
        return await self._session.send(
            "PATCH", f"pto/assignments/{user_id}", PtoAssignment, changes
        )


class PtoAllocations:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        year: int | None = None,
        user_ids: Sequence[int] | None = None,
        pto_type_ids: Sequence[int] | None = None,
    ) -> AsyncIterator[PtoAllocation]:
        return self._session.paginate(
            "pto/allocations",
            "pto_allocations",
            PtoAllocation,
            params={
                "year": year,
                "user_ids": _id_list(user_ids),
                "pto_type_ids": _id_list(pto_type_ids),
            },
        )

    async def update(
        self, changes: PtoAllocationUpdate
    ) -> PtoAllocation | PtoAllocationReset:
        """A reset confirmation instead of an allocation when no override
        remains."""
        outcome = await self._session.send(
            "PATCH", "pto/allocations", PtoAllocationOutcome, changes
        )
        return outcome.root

    async def bulk_update(
        self, items: Sequence[PtoAllocationBulkItem]
    ) -> PtoAllocationBulkResult:
        """Up to 2000 items, applied all or none."""
        return await self._session.send(
            "PATCH",
            "pto/allocations/bulk",
            PtoAllocationBulkResult,
            PtoAllocationBulkUpdate(allocations=list(items)),
        )
