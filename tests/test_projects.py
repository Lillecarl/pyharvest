from __future__ import annotations

import datetime as dt
import json
from decimal import Decimal

import pytest
import respx

from pyharvest import Harvest
from pyharvest.models.projects import (
    BillBy,
    BudgetBy,
    Project,
    ProjectCreate,
    ProjectUpdate,
    TaskAssignmentCreate,
    UserAssignmentUpdate,
)
from pyharvest.resources.projects import (
    Projects,
    Tags,
    TaskAssignments,
    UserAssignments,
)

from . import fixtures, fixtures_projects


@pytest.mark.anyio
async def test_list_renders_filters(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("projects").respond(
        json=fixtures.page("projects", [fixtures_projects.project()], None)
    )

    projects = [
        p
        async for p in Projects(harvest._session).list(
            is_active=False,
            client_id=2,
            updated_since=dt.datetime(2024, 3, 1, 12, tzinfo=dt.UTC),
        )
    ]

    assert projects[0].budget == Decimal("200.0")
    assert projects[0].bill_by is BillBy.PROJECT
    assert projects[0].budget_by is BudgetBy.PROJECT
    assert projects[0].tags[0].name == "Design"
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "is_active": "false",
        "client_id": "2",
        "updated_since": "2024-03-01T12:00:00Z",
    }


@pytest.mark.anyio
async def test_create_sends_enum_values(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("projects").respond(201, json=fixtures_projects.project())

    await Projects(harvest._session).create(
        ProjectCreate(
            client_id=2,
            name="Engine",
            is_billable=True,
            bill_by=BillBy.PROJECT,
            budget_by=BudgetBy.NONE,
            hourly_rate=100.0,
            starts_on=dt.date(2024, 1, 1),
        )
    )

    assert json.loads(route.calls.last.request.content) == {
        "client_id": 2,
        "name": "Engine",
        "is_billable": True,
        "bill_by": "Project",
        "budget_by": "none",
        "hourly_rate": 100.0,
        "starts_on": "2024-01-01",
    }


@pytest.mark.anyio
async def test_update_clears_tags_and_currency(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.patch("projects/3").respond(json=fixtures_projects.project())

    await Projects(harvest._session).update(3, ProjectUpdate(tag_ids=[], currency=None))

    assert json.loads(route.calls.last.request.content) == {
        "tag_ids": [],
        "currency": None,
    }


def test_unknown_bill_by_stays_str() -> None:
    project = Project.model_validate(fixtures_projects.project(bill_by="Milestones"))

    assert project.bill_by == "Milestones"


def test_tags_default_to_empty() -> None:
    raw = fixtures_projects.project()
    del raw["tags"]

    assert Project.model_validate(raw).tags == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("project_id", "path"),
    [(None, "user_assignments"), (3, "projects/3/user_assignments")],
)
async def test_user_assignments_list_path(
    harvest: Harvest, router: respx.MockRouter, project_id: int | None, path: str
) -> None:
    route = router.get(path).respond(
        json=fixtures.page(
            "user_assignments", [fixtures_projects.user_assignment()], None
        )
    )

    assignments = [
        a
        async for a in UserAssignments(harvest._session).list(
            project_id, user_id=1, is_active=True
        )
    ]

    assert assignments[0].hourly_rate == Decimal("75.5")
    assert assignments[0].project.code == "ENG"
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "user_id": "1",
        "is_active": "true",
    }


@pytest.mark.anyio
async def test_user_assignment_update(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.patch("projects/3/user_assignments/5").respond(
        json=fixtures_projects.user_assignment()
    )

    await UserAssignments(harvest._session).update(
        3, 5, UserAssignmentUpdate(budget=120.0, hourly_rate=None)
    )

    assert json.loads(route.calls.last.request.content) == {
        "budget": 120.0,
        "hourly_rate": None,
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("project_id", "path"),
    [(None, "task_assignments"), (3, "projects/3/task_assignments")],
)
async def test_task_assignments_list_path(
    harvest: Harvest, router: respx.MockRouter, project_id: int | None, path: str
) -> None:
    route = router.get(path).respond(
        json=fixtures.page(
            "task_assignments", [fixtures_projects.task_assignment()], None
        )
    )

    assignments = [
        a
        async for a in TaskAssignments(harvest._session).list(
            project_id, is_active=False
        )
    ]

    assert assignments[0].task.name == "Programming"
    assert assignments[0].project.code is None
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "is_active": "false",
    }


@pytest.mark.anyio
async def test_task_assignment_create_and_delete(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    create = router.post("projects/3/task_assignments").respond(
        201, json=fixtures_projects.task_assignment()
    )
    delete = router.delete("projects/3/task_assignments/6").respond(200)
    assignments = TaskAssignments(harvest._session)

    created = await assignments.create(
        3, TaskAssignmentCreate(task_id=4, billable=True, hourly_rate=75.5)
    )
    await assignments.delete(3, created.id)

    assert json.loads(create.calls.last.request.content) == {
        "task_id": 4,
        "billable": True,
        "hourly_rate": 75.5,
    }
    assert delete.called


@pytest.mark.anyio
async def test_tags_list(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("tags").respond(
        json=fixtures.page("tags", [fixtures_projects.tag()], None)
    )

    tags = [t async for t in Tags(harvest._session).list()]

    assert tags[0].name == "Design"
    assert dict(route.calls.last.request.url.params) == {"per_page": "2000"}
