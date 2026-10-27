from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.projects import Project, Tag, TaskAssignment, UserAssignment

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.projects import (
        ProjectCreate,
        ProjectUpdate,
        TaskAssignmentCreate,
        TaskAssignmentUpdate,
        UserAssignmentCreate,
        UserAssignmentUpdate,
    )


class Projects:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        is_active: bool | None = None,
        client_id: int | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[Project]:
        return self._session.paginate(
            "projects",
            "projects",
            Project,
            params={
                "is_active": is_active,
                "client_id": client_id,
                "updated_since": updated_since,
            },
        )

    async def get(self, project_id: int) -> Project:
        return await self._session.get(f"projects/{project_id}", Project)

    async def create(self, project: ProjectCreate) -> Project:
        return await self._session.send("POST", "projects", Project, project)

    async def update(self, project_id: int, changes: ProjectUpdate) -> Project:
        return await self._session.send(
            "PATCH", f"projects/{project_id}", Project, changes
        )

    async def delete(self, project_id: int) -> None:
        """Also deletes the project's time entries and expenses."""
        await self._session.delete(f"projects/{project_id}")


class UserAssignments:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        project_id: int | None = None,
        *,
        user_id: int | None = None,
        is_active: bool | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[UserAssignment]:
        """Every project's assignments, or one project's with ``project_id``."""
        path = (
            "user_assignments"
            if project_id is None
            else f"projects/{project_id}/user_assignments"
        )
        return self._session.paginate(
            path,
            "user_assignments",
            UserAssignment,
            params={
                "user_id": user_id,
                "is_active": is_active,
                "updated_since": updated_since,
            },
        )

    async def get(self, project_id: int, user_assignment_id: int) -> UserAssignment:
        return await self._session.get(
            f"projects/{project_id}/user_assignments/{user_assignment_id}",
            UserAssignment,
        )

    async def create(
        self, project_id: int, assignment: UserAssignmentCreate
    ) -> UserAssignment:
        return await self._session.send(
            "POST",
            f"projects/{project_id}/user_assignments",
            UserAssignment,
            assignment,
        )

    async def update(
        self,
        project_id: int,
        user_assignment_id: int,
        changes: UserAssignmentUpdate,
    ) -> UserAssignment:
        return await self._session.send(
            "PATCH",
            f"projects/{project_id}/user_assignments/{user_assignment_id}",
            UserAssignment,
            changes,
        )

    async def delete(self, project_id: int, user_assignment_id: int) -> None:
        await self._session.delete(
            f"projects/{project_id}/user_assignments/{user_assignment_id}"
        )


class TaskAssignments:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        project_id: int | None = None,
        *,
        is_active: bool | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[TaskAssignment]:
        """Every project's assignments, or one project's with ``project_id``."""
        path = (
            "task_assignments"
            if project_id is None
            else f"projects/{project_id}/task_assignments"
        )
        return self._session.paginate(
            path,
            "task_assignments",
            TaskAssignment,
            params={"is_active": is_active, "updated_since": updated_since},
        )

    async def get(self, project_id: int, task_assignment_id: int) -> TaskAssignment:
        return await self._session.get(
            f"projects/{project_id}/task_assignments/{task_assignment_id}",
            TaskAssignment,
        )

    async def create(
        self, project_id: int, assignment: TaskAssignmentCreate
    ) -> TaskAssignment:
        return await self._session.send(
            "POST",
            f"projects/{project_id}/task_assignments",
            TaskAssignment,
            assignment,
        )

    async def update(
        self,
        project_id: int,
        task_assignment_id: int,
        changes: TaskAssignmentUpdate,
    ) -> TaskAssignment:
        return await self._session.send(
            "PATCH",
            f"projects/{project_id}/task_assignments/{task_assignment_id}",
            TaskAssignment,
            changes,
        )

    async def delete(self, project_id: int, task_assignment_id: int) -> None:
        await self._session.delete(
            f"projects/{project_id}/task_assignments/{task_assignment_id}"
        )


class Tags:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self, *, updated_since: dt.datetime | None = None) -> AsyncIterator[Tag]:
        return self._session.paginate(
            "tags", "tags", Tag, params={"updated_since": updated_since}
        )
