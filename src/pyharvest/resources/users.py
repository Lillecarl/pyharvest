from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.users import User

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.users import UserCreate, UserUpdate


class Users:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        is_active: bool | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[User]:
        return self._session.paginate(
            "users",
            "users",
            User,
            params={"is_active": is_active, "updated_since": updated_since},
        )

    async def me(self) -> User:
        return await self._session.get("users/me", User)

    async def get(self, user_id: int) -> User:
        return await self._session.get(f"users/{user_id}", User)

    async def create(self, user: UserCreate) -> User:
        return await self._session.send("POST", "users", User, user)

    async def update(self, user_id: int, changes: UserUpdate) -> User:
        return await self._session.send("PATCH", f"users/{user_id}", User, changes)

    async def delete(self, user_id: int) -> None:
        await self._session.delete(f"users/{user_id}")
