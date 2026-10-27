from __future__ import annotations

import datetime as dt
from collections.abc import AsyncIterator, Mapping
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Final

import anyio
import httpx
from pydantic import BaseModel

from pyharvest.errors import error_for

if TYPE_CHECKING:
    from pydantic import JsonValue

type QueryValue = str | int | bool | dt.date | dt.datetime | Enum | None

MAX_PER_PAGE: Final = 2000


def query(params: Mapping[str, QueryValue]) -> dict[str, str | int]:
    """Drop unset parameters and render the rest the way Harvest parses them."""
    out: dict[str, str | int] = {}
    for key, value in params.items():
        match value:
            case None:
                continue
            case bool():
                out[key] = "true" if value else "false"
            case dt.datetime():
                out[key] = value.astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            case dt.date():
                out[key] = value.isoformat()
            case Enum():
                out[key] = str(value.value)
            case _:
                out[key] = value
    return out


def body(fields: Mapping[str, object]) -> dict[str, object]:
    """JSON body for a write, with unset (None) fields left out."""
    out: dict[str, object] = {}
    for key, value in fields.items():
        match value:
            case None:
                continue
            case BaseModel():
                out[key] = value.model_dump(mode="json", exclude_none=True)
            case dt.date() | dt.datetime() | Enum():
                out[key] = query({key: value})[key]
            case Decimal():
                out[key] = float(value)
            case _:
                out[key] = value
    return out


class Session:
    """HTTP transport shared by every resource: errors, retries, pagination."""

    def __init__(self, http: httpx.AsyncClient, *, max_retries: int) -> None:
        self.http = http
        self.max_retries = max_retries

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, QueryValue] | None = None,
        json: Mapping[str, object] | None = None,
    ) -> httpx.Response:
        # None, not {}: an empty params mapping makes httpx replace the URL's
        # own query, which drops the cursor from links.next.
        rendered = query(params) if params else None
        attempt = 0
        while True:
            response = await self.http.request(method, url, params=rendered, json=json)
            if response.status_code == 429 and attempt < self.max_retries:
                attempt += 1
                await anyio.sleep(float(response.headers.get("Retry-After", "1")))
                continue
            if response.is_error:
                raise error_for(response)
            return response

    async def get[M: BaseModel](
        self,
        url: str,
        model: type[M],
        *,
        params: Mapping[str, QueryValue] | None = None,
    ) -> M:
        response = await self.request("GET", url, params=params)
        return model.model_validate_json(response.content)

    async def send[M: BaseModel](
        self,
        method: str,
        url: str,
        model: type[M],
        *,
        json: Mapping[str, object] | None = None,
    ) -> M:
        response = await self.request(method, url, json=json)
        return model.model_validate_json(response.content)

    async def delete(self, url: str) -> None:
        await self.request("DELETE", url)

    async def paginate[M: BaseModel](
        self,
        url: str,
        key: str,
        model: type[M],
        *,
        params: Mapping[str, QueryValue] | None = None,
    ) -> AsyncIterator[M]:
        """Yield every record of a list endpoint, following ``links.next``.

        ``links.next`` is absolute and carries the cursor and every filter,
        so later requests send no params of their own.
        """
        next_url: str | None = url
        page_params: Mapping[str, QueryValue] | None = {
            "per_page": MAX_PER_PAGE,
            **(params or {}),
        }
        while next_url is not None:
            response = await self.request("GET", next_url, params=page_params)
            page: dict[str, JsonValue] = response.json()
            records = page[key]
            if not isinstance(records, list):
                raise TypeError(f"{url}: {key!r} is not a list")
            for record in records:
                yield model.model_validate(record)
            links = page.get("links")
            next_url = links.get("next") if isinstance(links, dict) else None
            if not isinstance(next_url, str | None):
                raise TypeError(f"{url}: links.next is not a string")
            page_params = None
