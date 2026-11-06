from __future__ import annotations

import datetime as dt
import mimetypes
import os
import re
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
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


# A receipt URL is on the account's subdomain, not on the API host.
FILE_HOST: Final = re.compile(r"[a-z0-9-]+\.harvestapp\.com")


@dataclass(frozen=True, slots=True)
class Attachment:
    """A file attached to a record, such as an expense receipt."""

    file_name: str
    content: bytes
    content_type: str

    @classmethod
    async def read(cls, path: str | os.PathLike[str]) -> Attachment:
        """Read a file, with its media type guessed from the extension."""
        file = anyio.Path(path)
        content_type, _ = mimetypes.guess_type(file.name)
        return cls(
            file.name,
            await file.read_bytes(),
            content_type or "application/octet-stream",
        )


def form(fields: Mapping[str, object]) -> dict[str, str]:
    """Render a dumped payload as multipart form fields."""
    out: dict[str, str] = {}
    for key, value in fields.items():
        match value:
            case None:
                # A form part has no null; "" would set an empty string.
                raise ValueError(f"{key}: multipart cannot send null")
            case bool():
                out[key] = "true" if value else "false"
            case str() | int() | float():
                out[key] = str(value)
            case _:
                raise TypeError(f"{key}: multipart cannot send {type(value).__name__}")
    return out


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
                # A naive datetime would silently take the machine's offset.
                if value.tzinfo is None:
                    raise ValueError(f"{key}: datetime needs a timezone")
                out[key] = value.astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            case dt.date():
                out[key] = value.isoformat()
            case Enum():
                out[key] = str(value.value)
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
        data: Mapping[str, str] | None = None,
        files: Mapping[str, Attachment] | None = None,
    ) -> httpx.Response:
        # None, not {}: an empty params mapping makes httpx replace the URL's
        # own query, which drops the cursor from links.next.
        rendered = query(params or {}) or None
        parts = (
            {k: (f.file_name, f.content, f.content_type) for k, f in files.items()}
            if files
            else None
        )
        attempt = 0
        while True:
            response = await self.http.request(
                method, url, params=rendered, json=json, data=data, files=parts
            )
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
        payload: BaseModel | None = None,
        *,
        files: Mapping[str, Attachment] | None = None,
    ) -> M:
        """With ``files``, the payload goes as form fields of a multipart body."""
        body = None
        if payload is not None:
            # exclude_unset: a field passed as None is sent as null, to clear it.
            body = payload.model_dump(mode="json", exclude_unset=True)
        if files:
            response = await self.request(
                method, url, data=form(body or {}), files=files
            )
        else:
            response = await self.request(method, url, json=body)
        return model.model_validate_json(response.content)

    async def delete(self, url: str) -> None:
        await self.request("DELETE", url)

    async def download(self, url: str) -> httpx.Response:
        """GET an absolute file URL from Harvest, with the token.

        Refuses any other host, so a URL in a response cannot send the token
        elsewhere. Redirects are not followed, and a 3xx raises.
        """
        target = httpx.URL(url)
        if target.scheme != "https" or not FILE_HOST.fullmatch(target.host):
            raise ValueError(f"not a Harvest file URL: {url}")
        response = await self.request("GET", url)
        if response.status_code != 200:
            raise error_for(response)
        return response

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
