from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.projects import BudgetBy
from pyharvest.models.reports import (
    DetailedTimeGroupBy,
    ExportFormat,
    ExportStatus,
    ProjectBudgetReportResult,
    ReportExportCreate,
    ReportGenerate,
    SavedReportCreate,
    SavedReportUpdate,
)
from pyharvest.resources.reports import Reports

from . import fixtures_reports as fixtures

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_time_projects_renders_iso_dates(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.get("reports/time/projects").respond(
        json=fixtures.page("results", [fixtures.time_by_project()], None)
    )

    rows = [
        r
        async for r in Reports(harvest._session).time_projects(
            from_=dt.date(2024, 1, 1), to=dt.date(2024, 12, 31), include_forecast=True
        )
    ]

    assert rows[0].total_hours == Decimal("4.5")
    assert rows[0].billable_amount is None
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "from": "2024-01-01",
        "to": "2024-12-31",
        "include_forecast": "true",
    }


@pytest.mark.anyio
async def test_time_detailed_follows_pages(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    second = "https://api.harvestapp.com/v2/reports/time/detailed?cursor=abc"
    first_route = router.get("reports/time/detailed", params={"from": "2024-03-01"})
    first_route.respond(
        json=fixtures.page("results", [fixtures.detailed_time_row()], second)
    )
    router.get(second).respond(
        json=fixtures.page("results", [fixtures.detailed_time_row(id=101)], None)
    )

    rows = [
        r
        async for r in Reports(harvest._session).time_detailed(
            from_=dt.date(2024, 3, 1),
            to=dt.date(2024, 3, 31),
            is_billed=False,
            group_by=DetailedTimeGroupBy.PROJECTS,
        )
    ]

    assert [r.id for r in rows] == [100, 101]
    assert rows[0].spent_date == dt.date(2024, 3, 1)
    assert dict(first_route.calls.last.request.url.params) == {
        "per_page": "2000",
        "from": "2024-03-01",
        "to": "2024-03-31",
        "is_billed": "false",
        "group_by": "projects",
    }


def test_project_budget_hides_money_and_keeps_unknown_budget_by() -> None:
    hidden = ProjectBudgetReportResult.model_validate(
        fixtures.project_budget(
            budget_by="project_cost",
            budget=None,
            budget_spent=None,
            budget_remaining=None,
        )
    )
    unknown = ProjectBudgetReportResult.model_validate(
        fixtures.project_budget(budget_by="per_week")
    )

    assert hidden.budget_by is BudgetBy.PROJECT_COST
    assert hidden.budget is None
    assert unknown.budget_by == "per_week"


@pytest.mark.anyio
async def test_saved_create_and_update_bodies(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    create = router.post("reports/saved").respond(201, json=fixtures.saved_report())
    update = router.patch("reports/saved/7").respond(json=fixtures.saved_report())
    reports = Reports(harvest._session)
    configuration = {"subject": "time", "columns": ["hours"]}

    created = await reports.saved_create(
        SavedReportCreate(name="By client", configuration=configuration)
    )
    await reports.saved_update(7, SavedReportUpdate(description=None, lock_version=3))

    assert created.configuration["levels"] == [{"kind": "column", "id": "client"}]
    assert json.loads(create.calls.last.request.content) == {
        "name": "By client",
        "configuration": configuration,
    }
    assert json.loads(update.calls.last.request.content) == {
        "description": None,
        "lock_version": 3,
    }


@pytest.mark.anyio
async def test_generate_unwraps_envelope(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("reports/generate").respond(json=fixtures.generated_report())

    report = await Reports(harvest._session).generate(
        ReportGenerate(configuration={"subject": "time"}, limit=10)
    )

    assert report.rows[0]["hours"] == 12.5
    assert report.row_currencies is None
    assert json.loads(route.calls.last.request.content) == {
        "configuration": {"subject": "time"},
        "limit": 10,
    }


@pytest.mark.anyio
async def test_run_saved_sends_limit(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.get("reports/generated/7").respond(
        json=fixtures.generated_report(report_id=7, overflow=True)
    )

    report = await Reports(harvest._session).run_saved(7, limit=500)

    assert report.report_id == 7
    assert dict(route.calls.last.request.url.params) == {"limit": "500"}


@pytest.mark.anyio
async def test_export_create_body(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("reports/exports").respond(201, json=fixtures.report_export())

    export = await Reports(harvest._session).export_create(
        ReportExportCreate(
            type="detailed_time_report",
            export_format=ExportFormat.CSV,
            params={"from": "2024-03-01", "till": "2024-03-31"},
        )
    )

    assert export.status is ExportStatus.PENDING
    assert export.format is ExportFormat.CSV
    assert json.loads(route.calls.last.request.content) == {
        "type": "detailed_time_report",
        "export_format": "csv",
        "params": {"from": "2024-03-01", "till": "2024-03-31"},
    }


@pytest.mark.anyio
async def test_export_download_returns_bytes(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("reports/exports/42/download").respond(
        content=b"date,hours\n2024-03-01,2.25\n",
        headers={"content-type": "text/csv"},
    )

    data = await Reports(harvest._session).export_download(42)

    assert data == b"date,hours\n2024-03-01,2.25\n"


@pytest.mark.anyio
async def test_export_download_refuses_redirect(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("reports/exports/42/download").respond(
        302, headers={"location": "https://example.com/file.csv"}
    )

    with pytest.raises(RuntimeError, match="302"):
        await Reports(harvest._session).export_download(42)
