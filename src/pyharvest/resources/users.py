from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest._session import body
from pyharvest.models.users import User

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator, Sequence
    from decimal import Decimal

    from pyharvest._session import Session


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

    async def create(
        self,
        *,
        first_name: str,
        last_name: str,
        email: str,
        timezone: str | None = None,
        has_access_to_all_future_projects: bool | None = None,
        is_contractor: bool | None = None,
        is_active: bool | None = None,
        saml_exempt: bool | None = None,
        weekly_capacity: int | None = None,
        default_hourly_rate: Decimal | None = None,
        cost_rate: Decimal | None = None,
        roles: Sequence[str] | None = None,
        access_roles: Sequence[str] | None = None,
        permissions_profile: str | None = None,
        custom_role_id: int | None = None,
    ) -> User:
        return await self._session.send(
            "POST",
            "users",
            User,
            json=body(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "timezone": timezone,
                    "has_access_to_all_future_projects": has_access_to_all_future_projects,
                    "is_contractor": is_contractor,
                    "is_active": is_active,
                    "saml_exempt": saml_exempt,
                    "weekly_capacity": weekly_capacity,
                    "default_hourly_rate": default_hourly_rate,
                    "cost_rate": cost_rate,
                    "roles": roles,
                    "access_roles": access_roles,
                    "permissions_profile": permissions_profile,
                    "custom_role_id": custom_role_id,
                }
            ),
        )

    async def update(
        self,
        user_id: int,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        timezone: str | None = None,
        has_access_to_all_future_projects: bool | None = None,
        is_contractor: bool | None = None,
        is_active: bool | None = None,
        saml_exempt: bool | None = None,
        weekly_capacity: int | None = None,
        default_hourly_rate: Decimal | None = None,
        cost_rate: Decimal | None = None,
        roles: Sequence[str] | None = None,
        access_roles: Sequence[str] | None = None,
        permissions_profile: str | None = None,
        custom_role_id: int | None = None,
    ) -> User:
        return await self._session.send(
            "PATCH",
            f"users/{user_id}",
            User,
            json=body(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "timezone": timezone,
                    "has_access_to_all_future_projects": has_access_to_all_future_projects,
                    "is_contractor": is_contractor,
                    "is_active": is_active,
                    "saml_exempt": saml_exempt,
                    "weekly_capacity": weekly_capacity,
                    "default_hourly_rate": default_hourly_rate,
                    "cost_rate": cost_rate,
                    "roles": roles,
                    "access_roles": access_roles,
                    "permissions_profile": permissions_profile,
                    "custom_role_id": custom_role_id,
                }
            ),
        )

    async def delete(self, user_id: int) -> None:
        await self._session.delete(f"users/{user_id}")
