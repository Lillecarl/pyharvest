from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.roles import CustomRole, Permission, Role

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.roles import (
        CustomRoleCreate,
        CustomRoleUpdate,
        RoleCreate,
        RoleUpdate,
    )


class Roles:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> AsyncIterator[Role]:
        return self._session.paginate("roles", "roles", Role)

    async def get(self, role_id: int) -> Role:
        return await self._session.get(f"roles/{role_id}", Role)

    async def create(self, role: RoleCreate) -> Role:
        return await self._session.send("POST", "roles", Role, role)

    async def update(self, role_id: int, changes: RoleUpdate) -> Role:
        return await self._session.send("PATCH", f"roles/{role_id}", Role, changes)

    async def delete(self, role_id: int) -> None:
        await self._session.delete(f"roles/{role_id}")


class CustomRoles:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[CustomRole]:
        return self._session.paginate(
            "custom_roles",
            "custom_roles",
            CustomRole,
            params={"updated_since": updated_since},
        )

    async def get(self, custom_role_id: int) -> CustomRole:
        return await self._session.get(f"custom_roles/{custom_role_id}", CustomRole)

    async def create(self, role: CustomRoleCreate) -> CustomRole:
        return await self._session.send("POST", "custom_roles", CustomRole, role)

    async def update(
        self, custom_role_id: int, changes: CustomRoleUpdate
    ) -> CustomRole:
        return await self._session.send(
            "PATCH", f"custom_roles/{custom_role_id}", CustomRole, changes
        )

    async def delete(self, custom_role_id: int) -> CustomRole:
        """Return the deleted role; its users fall back to ``member``."""
        return await self._session.send(
            "DELETE", f"custom_roles/{custom_role_id}", CustomRole
        )


class Permissions:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[Permission]:
        return self._session.paginate(
            "permissions",
            "permissions",
            Permission,
            params={"updated_since": updated_since},
        )
