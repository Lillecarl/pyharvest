from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.gusto import (
    GustoEntityType,
    GustoMonthPosition,
    GustoReminderFrequency,
    GustoSettingsUpdate,
    GustoSyncProjectInput,
    GustoSyncRange,
    GustoSyncReminderInput,
    GustoSyncRunCreate,
    GustoSyncRunStatus,
    GustoUserMappingCreate,
    GustoWeekday,
)
from pyharvest.resources.gusto import GustoIntegration, GustoSyncRuns

from . import fixtures_gusto

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_preview_body(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("integrations/gusto/sync_runs/preview").respond(
        json=fixtures_gusto.sync_preview()
    )

    preview = await GustoSyncRuns(harvest._session).preview(
        GustoSyncRange(date_range_start=dt.date(2024, 3, 4))
    )

    assert preview.projects[0].total_hours == Decimal("12.5")
    assert preview.projects[0].available_jobs[0].uuid == "job-1"
    assert json.loads(route.calls.last.request.content) == {
        "date_range_start": "2024-03-04"
    }


@pytest.mark.anyio
async def test_create_and_get_run(harvest: Harvest, router: respx.MockRouter) -> None:
    create = router.post("integrations/gusto/sync_runs").respond(
        201, json=fixtures_gusto.sync_run()
    )
    router.get("integrations/gusto/sync_runs/4000").respond(
        json=fixtures_gusto.sync_run(status="completed")
    )
    runs = GustoSyncRuns(harvest._session)

    created = await runs.create(
        GustoSyncRunCreate(
            gusto_payroll_uuid="payroll-1",
            projects=[GustoSyncProjectInput(user_mapping_id=50, project_id=3)],
        )
    )
    fetched = await runs.get(4000)

    assert created.workweek_anchor is GustoWeekday.SUNDAY
    assert fetched.status is GustoSyncRunStatus.COMPLETED
    assert json.loads(create.calls.last.request.content) == {
        "gusto_payroll_uuid": "payroll-1",
        "projects": [{"user_mapping_id": 50, "project_id": 3}],
    }


@pytest.mark.anyio
async def test_update_settings_body(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.patch("integrations/gusto/settings").respond(
        json=fixtures_gusto.settings()
    )

    settings = await GustoIntegration(harvest._session).update(
        GustoSettingsUpdate(
            workweek_anchor=GustoWeekday.MONDAY,
            sync_reminder=GustoSyncReminderInput(
                enabled=True,
                frequency=GustoReminderFrequency.SEMIMONTHLY,
                semimonthly_position_one=GustoMonthPosition.FIRST_DAY,
                semimonthly_position_two=GustoMonthPosition.MID_MONTH,
            ),
        )
    )

    assert settings.sync_reminder.weekday is GustoWeekday.MONDAY
    assert settings.user_mappings[0].gusto_entity_type is GustoEntityType.EMPLOYEE
    assert json.loads(route.calls.last.request.content) == {
        "workweek_anchor": "Monday",
        "sync_reminder": {
            "enabled": True,
            "frequency": "semimonthly",
            "semimonthly_position_one": "first_day",
            "semimonthly_position_two": "mid_month",
        },
    }


@pytest.mark.anyio
async def test_user_mappings(harvest: Harvest, router: respx.MockRouter) -> None:
    bulk = router.post("integrations/gusto/user_mappings/bulk_create").respond(
        json={
            "created_count": 1,
            "created": [fixtures_gusto.user_mapping()],
            "failed": [{"user_id": 2, "message": "Already linked"}],
        }
    )
    delete = router.delete("integrations/gusto/user_mappings/50").respond(
        json=fixtures_gusto.user_mapping()
    )
    gusto = GustoIntegration(harvest._session)

    result = await gusto.bulk_create_user_mappings(
        [
            GustoUserMappingCreate(
                user_id=1,
                gusto_entity_type=GustoEntityType.CONTRACTOR,
                gusto_entity_uuid="person-1",
            )
        ]
    )
    deleted = await gusto.delete_user_mapping(50)

    assert result.failed[0].message == "Already linked"
    assert deleted.id == 50
    assert delete.called
    assert json.loads(bulk.calls.last.request.content) == {
        "mappings": [
            {
                "user_id": 1,
                "gusto_entity_type": "Contractor",
                "gusto_entity_uuid": "person-1",
            }
        ]
    }
