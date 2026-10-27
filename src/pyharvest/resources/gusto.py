from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.gusto import (
    GustoSettings,
    GustoSyncPreview,
    GustoSyncRun,
    GustoUserMapping,
    GustoUserMappingBulkCreate,
    GustoUserMappingBulkResult,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyharvest._session import Session
    from pyharvest.models.gusto import (
        GustoSettingsUpdate,
        GustoSyncRange,
        GustoSyncRunCreate,
        GustoUserMappingCreate,
    )


class GustoSyncRuns:
    def __init__(self, session: Session) -> None:
        self._session = session

    async def preview(self, sync_range: GustoSyncRange) -> GustoSyncPreview:
        """What a run over the range would post. Creates nothing."""
        return await self._session.send(
            "POST",
            "integrations/gusto/sync_runs/preview",
            GustoSyncPreview,
            sync_range,
        )

    async def create(self, run: GustoSyncRunCreate) -> GustoSyncRun:
        return await self._session.send(
            "POST", "integrations/gusto/sync_runs", GustoSyncRun, run
        )

    async def get(self, sync_run_id: int) -> GustoSyncRun:
        return await self._session.get(
            f"integrations/gusto/sync_runs/{sync_run_id}", GustoSyncRun
        )


class GustoIntegration:
    """The Gusto connection's settings and its teammate links."""

    def __init__(self, session: Session) -> None:
        self._session = session

    async def get(self) -> GustoSettings:
        return await self._session.get("integrations/gusto/settings", GustoSettings)

    async def update(self, changes: GustoSettingsUpdate) -> GustoSettings:
        return await self._session.send(
            "PATCH", "integrations/gusto/settings", GustoSettings, changes
        )

    async def create_user_mapping(
        self, mapping: GustoUserMappingCreate
    ) -> GustoUserMapping:
        return await self._session.send(
            "POST", "integrations/gusto/user_mappings", GustoUserMapping, mapping
        )

    async def bulk_create_user_mappings(
        self, mappings: Sequence[GustoUserMappingCreate]
    ) -> GustoUserMappingBulkResult:
        return await self._session.send(
            "POST",
            "integrations/gusto/user_mappings/bulk_create",
            GustoUserMappingBulkResult,
            GustoUserMappingBulkCreate(mappings=list(mappings)),
        )

    async def delete_user_mapping(self, user_mapping_id: int) -> GustoUserMapping:
        return await self._session.send(
            "DELETE",
            f"integrations/gusto/user_mappings/{user_mapping_id}",
            GustoUserMapping,
        )
