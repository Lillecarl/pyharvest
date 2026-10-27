from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal
from typing import TYPE_CHECKING

import httpx
import pytest

from pyharvest.models.pto import (
    HolidayCalendarEntryCreate,
    PtoAccrualType,
    PtoAllocation,
    PtoAllocationBulkItem,
    PtoAllocationReset,
    PtoAllocationUpdate,
    PtoAssignmentUpdate,
    PtoConflictResolution,
    TimeOffRequestCreate,
    TimeOffRequestStatus,
    WorkScheduleUpdate,
)
from pyharvest.resources.pto import (
    HolidayCalendarEntries,
    HolidayCalendars,
    PtoAllocations,
    PtoAssignments,
    TimeOffBalances,
    TimeOffPolicies,
    TimeOffRequests,
    WorkSchedules,
)

from . import fixtures, fixtures_pto

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_requests_list_renders_filters(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.get("pto/requests").respond(
        json=fixtures.page("pto_requests", [fixtures_pto.time_off_request()], None)
    )

    found = [
        r
        async for r in TimeOffRequests(harvest._session).list(
            status=TimeOffRequestStatus.PENDING,
            pto_type_id=20,
            from_=dt.date(2024, 3, 1),
            to=dt.date(2024, 3, 31),
        )
    ]

    request = found[0]
    assert request.status is TimeOffRequestStatus.PENDING
    assert request.request_days[1].day_fraction == Decimal("0.5")
    assert request.pto_type.color == "blue"
    assert request.coverage_warnings is not None
    assert request.coverage_warnings[0].dates == [dt.date(2024, 3, 4)]
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "status": "pending",
        "pto_type_id": "20",
        "from": "2024-03-01",
        "to": "2024-03-31",
    }


@pytest.mark.anyio
async def test_request_create_body(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("pto/requests").respond(
        201, json=fixtures_pto.time_off_request()
    )

    await TimeOffRequests(harvest._session).create(
        TimeOffRequestCreate(
            pto_type_id=20,
            start_date=dt.date(2024, 3, 4),
            end_date=dt.date(2024, 3, 5),
            end_time_minutes=780,
            conflict_resolution=PtoConflictResolution.REPLACE,
        )
    )

    assert json.loads(route.calls.last.request.content) == {
        "pto_type_id": 20,
        "start_date": "2024-03-04",
        "end_date": "2024-03-05",
        "end_time_minutes": 780,
        "conflict_resolution": "replace",
    }


@pytest.mark.anyio
async def test_request_review_actions(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    approve = router.post("pto/requests/30/approve").respond(
        json=fixtures_pto.time_off_request(status="approved")
    )
    decline = router.post("pto/requests/30/decline").respond(
        json=fixtures_pto.time_off_request(status="declined")
    )
    changes = router.post("pto/requests/30/request_changes").respond(
        json=fixtures_pto.time_off_request(status="changes_requested")
    )
    cancel = router.delete("pto/requests/30").respond(
        json=fixtures_pto.time_off_request(status="cancelled")
    )
    requests = TimeOffRequests(harvest._session)

    assert (await requests.approve(30)).status is TimeOffRequestStatus.APPROVED
    await requests.decline(30)
    await requests.request_changes(30, "Move it a week")
    assert (await requests.cancel(30)).status is TimeOffRequestStatus.CANCELLED

    assert approve.calls.last.request.content == b""
    assert decline.calls.last.request.content == b""
    assert json.loads(changes.calls.last.request.content) == {
        "reason": "Move it a week"
    }
    assert cancel.called


@pytest.mark.anyio
async def test_bulk_decline(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("pto/requests/decline").respond(
        json={
            "pto_requests": [fixtures_pto.time_off_request(status="declined")],
            "skipped_ids": [33],
        }
    )

    result = await TimeOffRequests(harvest._session).decline_many(
        [30, 33], reason="Coverage"
    )

    assert result.skipped_ids == [33]
    assert json.loads(route.calls.last.request.content) == {
        "ids": [30, 33],
        "reason": "Coverage",
    }


@pytest.mark.anyio
async def test_work_schedule_update_and_deactivate(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    update = router.patch("pto/work_schedules/10").respond(
        json=fixtures_pto.work_schedule()
    )
    router.delete("pto/work_schedules/10").respond(
        json=fixtures_pto.work_schedule(is_active=False)
    )
    schedules = WorkSchedules(harvest._session)

    updated = await schedules.update(10, WorkScheduleUpdate(friday_hours=4.5))
    deactivated = await schedules.deactivate(10)

    assert updated.weekly_hours == Decimal("32.0")
    assert deactivated.is_active is False
    assert json.loads(update.calls.last.request.content) == {"friday_hours": 4.5}


@pytest.mark.anyio
async def test_policy_list_and_delete_with_history(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    listing = router.get("pto/types").respond(
        json=fixtures.page("pto_types", [fixtures_pto.time_off_policy()], None)
    )
    delete = router.delete("pto/types/20").respond(204)
    policies = TimeOffPolicies(harvest._session)

    found = [p async for p in policies.list(is_active=False)]
    await policies.delete_with_history(20)

    assert found[0].accrual_type is PtoAccrualType.FIXED
    assert found[0].accrual_leave_hours is None
    assert dict(listing.calls.last.request.url.params) == {
        "per_page": "2000",
        "is_active": "false",
    }
    assert dict(delete.calls.last.request.url.params) == {
        "keep_history": "false",
        "confirm_delete_history": "1",
    }


@pytest.mark.anyio
async def test_balances(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("pto/balances").respond(json=fixtures_pto.balance_sheet())

    sheet = await TimeOffBalances(harvest._session).get(user_id=1, year=2024)

    assert sheet.balances[0].used_fraction == Decimal("0.3704")
    assert dict(route.calls.last.request.url.params) == {
        "user_id": "1",
        "year": "2024",
    }


@pytest.mark.anyio
async def test_holiday_calendars_and_entries(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("pto/holiday_calendars").respond(
        json=fixtures.page(
            "pto_holiday_calendars", [fixtures_pto.holiday_calendar()], None
        )
    )
    router.get("pto/holiday_calendars/40/entries").respond(
        json=fixtures.page(
            "pto_holiday_calendar_entries",
            [fixtures_pto.holiday_calendar_entry()],
            None,
        )
    )
    create = router.post("pto/holiday_calendars/40/entries").respond(
        201, json=fixtures_pto.holiday_calendar_entry()
    )
    router.delete("pto/holiday_calendars/40/entries/41").respond(
        json=fixtures_pto.holiday_calendar_entry()
    )
    entries = HolidayCalendarEntries(harvest._session)

    calendars = [c async for c in HolidayCalendars(harvest._session).list()]
    listed = [e async for e in entries.list(40)]
    await entries.create(
        40,
        HolidayCalendarEntryCreate(
            name="Summer closure",
            date_mode="range",
            start_date=dt.date(2024, 7, 1),
            end_date=dt.date(2024, 7, 5),
        ),
    )
    deleted = await entries.delete(40, 41)

    assert calendars[0].entries[0].date == dt.date(2024, 1, 1)
    assert listed[0].pto_holiday_calendar_id == 40
    assert deleted.id == 41
    assert json.loads(create.calls.last.request.content) == {
        "name": "Summer closure",
        "date_mode": "range",
        "start_date": "2024-07-01",
        "end_date": "2024-07-05",
    }


@pytest.mark.anyio
async def test_assignments(harvest: Harvest, router: respx.MockRouter) -> None:
    listing = router.get("pto/assignments").respond(
        json={"assignments": [fixtures_pto.assignment()]}
    )
    update = router.patch("pto/assignments/1").respond(json=fixtures_pto.assignment())
    assignments = PtoAssignments(harvest._session)

    found = [a async for a in assignments.list(user_ids=[1, 2])]
    await assignments.update(1, PtoAssignmentUpdate(work_schedule_id=None))

    assert found[0].work_schedule is None
    assert found[0].effective_work_schedule is not None
    assert found[0].effective_work_schedule.weekly_hours == Decimal("40.0")
    assert dict(listing.calls.last.request.url.params) == {
        "per_page": "2000",
        "user_ids": "1,2",
    }
    assert json.loads(update.calls.last.request.content) == {"work_schedule_id": None}


@pytest.mark.anyio
async def test_allocation_update_returns_either_shape(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.patch("pto/allocations").mock(
        side_effect=[
            httpx.Response(200, json=fixtures_pto.allocation()),
            httpx.Response(200, json=fixtures_pto.allocation_reset()),
        ]
    )
    allocations = PtoAllocations(harvest._session)

    saved = await allocations.update(
        PtoAllocationUpdate(user_id=1, pto_type_id=20, days_per_year=28.0)
    )
    reset = await allocations.update(
        PtoAllocationUpdate(user_id=1, pto_type_id=20, reset_to_default=True)
    )

    assert isinstance(saved, PtoAllocation)
    assert saved.days_per_year == Decimal("28.0")
    assert isinstance(reset, PtoAllocationReset)
    assert reset.customized is False
    assert json.loads(route.calls.last.request.content) == {
        "user_id": 1,
        "pto_type_id": 20,
        "reset_to_default": True,
    }


@pytest.mark.anyio
async def test_allocation_bulk_update(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.patch("pto/allocations/bulk").respond(
        json={
            "pto_allocations": [
                fixtures_pto.allocation(
                    id=None,
                    created_at=None,
                    updated_at=None,
                    deferred_accrual=None,
                    effective_deferred_accrual=False,
                    holiday_calendar=None,
                )
            ]
        }
    )

    result = await PtoAllocations(harvest._session).bulk_update(
        [
            PtoAllocationBulkItem(
                user_id=1,
                pto_type_id=20,
                year=2024,
                days_per_year=None,
                holiday_calendar_id="none",
            )
        ]
    )

    assert result.pto_allocations[0].id is None
    assert json.loads(route.calls.last.request.content) == {
        "allocations": [
            {
                "user_id": 1,
                "pto_type_id": 20,
                "year": 2024,
                "days_per_year": None,
                "holiday_calendar_id": "none",
            }
        ]
    }
