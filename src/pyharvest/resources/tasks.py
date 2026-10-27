from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.tasks import Task

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.tasks import TaskCreate, TaskUpdate


class Tasks:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        is_active: bool | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[Task]:
        return self._session.paginate(
            "tasks",
            "tasks",
            Task,
            params={"is_active": is_active, "updated_since": updated_since},
        )

    async def get(self, task_id: int) -> Task:
        return await self._session.get(f"tasks/{task_id}", Task)

    async def create(self, task: TaskCreate) -> Task:
        return await self._session.send("POST", "tasks", Task, task)

    async def update(self, task_id: int, changes: TaskUpdate) -> Task:
        return await self._session.send("PATCH", f"tasks/{task_id}", Task, changes)

    async def delete(self, task_id: int) -> None:
        await self._session.delete(f"tasks/{task_id}")
