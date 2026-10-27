from __future__ import annotations

from typing import TYPE_CHECKING, Final, Self

import httpx

from pyharvest.models import User

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
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Harvest-Account-Id": account_id,
                "User-Agent": user_agent,
            },
            transport=transport,
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
        await self._http.aclose()

    async def me(self) -> User:
        response = await self._http.get("users/me")
        response.raise_for_status()
        return User.model_validate_json(response.content)
