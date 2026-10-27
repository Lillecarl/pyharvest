from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.imports import Import

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session


class Imports:
    """CSV import runs. Starting one needs a multipart upload, which this
    client does not send."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[Import]:
        """Runs created in the last 30 days, newest first."""
        return self._session.paginate(
            "imports", "imports", Import, params={"updated_since": updated_since}
        )

    async def get(self, import_id: int) -> Import:
        return await self._session.get(f"imports/{import_id}", Import)

    async def csv_errors(self, import_id: int) -> str:
        """The failed rows as CSV, under the import type's header row.

        Harvest answers 404 when ``csv_errors_available`` is false.
        """
        response = await self._session.request("GET", f"imports/{import_id}/csv_errors")
        return response.text

    async def revert(self, import_id: int) -> Import:
        return await self._session.send("POST", f"imports/{import_id}/revert", Import)
