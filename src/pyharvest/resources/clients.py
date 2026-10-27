from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.clients import Client, Contact

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.clients import (
        ClientCreate,
        ClientUpdate,
        ContactCreate,
        ContactUpdate,
    )


class Clients:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        is_active: bool | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[Client]:
        return self._session.paginate(
            "clients",
            "clients",
            Client,
            params={"is_active": is_active, "updated_since": updated_since},
        )

    async def get(self, client_id: int) -> Client:
        return await self._session.get(f"clients/{client_id}", Client)

    async def create(self, client: ClientCreate) -> Client:
        return await self._session.send("POST", "clients", Client, client)

    async def update(self, client_id: int, changes: ClientUpdate) -> Client:
        return await self._session.send(
            "PATCH", f"clients/{client_id}", Client, changes
        )

    async def delete(self, client_id: int) -> None:
        await self._session.delete(f"clients/{client_id}")


class Contacts:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        client_id: int | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[Contact]:
        return self._session.paginate(
            "contacts",
            "contacts",
            Contact,
            params={"client_id": client_id, "updated_since": updated_since},
        )

    async def get(self, contact_id: int) -> Contact:
        return await self._session.get(f"contacts/{contact_id}", Contact)

    async def create(self, contact: ContactCreate) -> Contact:
        return await self._session.send("POST", "contacts", Contact, contact)

    async def update(self, contact_id: int, changes: ContactUpdate) -> Contact:
        return await self._session.send(
            "PATCH", f"contacts/{contact_id}", Contact, changes
        )

    async def delete(self, contact_id: int) -> None:
        await self._session.delete(f"contacts/{contact_id}")
