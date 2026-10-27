from __future__ import annotations

import os
from typing import TYPE_CHECKING, Final, Self

import httpx

from pyharvest._session import Session
from pyharvest.resources import (
    Clients,
    CompanySettings,
    Contacts,
    TimeEntries,
    Users,
)

if TYPE_CHECKING:
    from types import TracebackType

BASE_URL: Final = "https://api.harvestapp.com/v2/"


class Harvest:
    """Async client for the Harvest API v2.

    Harvest requires a User-Agent that names the application and a contact,
    for example ``"MyApp (me@example.com)"``.
    """

    def __init__(
        self,
        *,
        access_token: str,
        account_id: str,
        user_agent: str,
        base_url: str = BASE_URL,
        max_retries: int = 3,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        http = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Harvest-Account-Id": account_id,
                "User-Agent": user_agent,
            },
            transport=transport,
        )
        self._session = Session(http, max_retries=max_retries)
        self.clients: Final = Clients(self._session)
        self.company: Final = CompanySettings(self._session)
        self.contacts: Final = Contacts(self._session)
        self.time_entries: Final = TimeEntries(self._session)
        self.users: Final = Users(self._session)

    @classmethod
    def from_env(cls, *, user_agent: str) -> Self:
        """Read ``HARVEST_TOKEN`` and ``HARVEST_ACCOUNT`` from the environment."""
        return cls(
            access_token=os.environ["HARVEST_TOKEN"],
            account_id=os.environ["HARVEST_ACCOUNT"],
            user_agent=user_agent,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._session.http.aclose()
