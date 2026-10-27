from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.estimates import (
    Estimate,
    EstimateEvent,
    EstimateEventType,
    EstimateItemCategory,
    EstimateMessage,
)

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.estimates import (
        EstimateCreate,
        EstimateItemCategoryCreate,
        EstimateItemCategoryUpdate,
        EstimateMessageCreate,
        EstimateState,
        EstimateUpdate,
    )


class Estimates:
    """Line items are added, changed and removed through ``update``."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        client_id: int | None = None,
        updated_since: dt.datetime | None = None,
        from_: dt.date | None = None,
        to: dt.date | None = None,
        state: EstimateState | None = None,
    ) -> AsyncIterator[Estimate]:
        return self._session.paginate(
            "estimates",
            "estimates",
            Estimate,
            params={
                "client_id": client_id,
                "updated_since": updated_since,
                "from": from_,
                "to": to,
                "state": state,
            },
        )

    async def get(self, estimate_id: int) -> Estimate:
        return await self._session.get(f"estimates/{estimate_id}", Estimate)

    async def create(self, estimate: EstimateCreate) -> Estimate:
        return await self._session.send("POST", "estimates", Estimate, estimate)

    async def update(self, estimate_id: int, changes: EstimateUpdate) -> Estimate:
        return await self._session.send(
            "PATCH", f"estimates/{estimate_id}", Estimate, changes
        )

    async def delete(self, estimate_id: int) -> None:
        await self._session.delete(f"estimates/{estimate_id}")


class EstimateMessages:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, estimate_id: int, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[EstimateMessage]:
        return self._session.paginate(
            f"estimates/{estimate_id}/messages",
            "estimate_messages",
            EstimateMessage,
            params={"updated_since": updated_since},
        )

    async def create(
        self, estimate_id: int, message: EstimateMessageCreate
    ) -> EstimateMessage:
        return await self._session.send(
            "POST", f"estimates/{estimate_id}/messages", EstimateMessage, message
        )

    async def delete(self, estimate_id: int, message_id: int) -> None:
        await self._session.delete(f"estimates/{estimate_id}/messages/{message_id}")

    async def _event(
        self, estimate_id: int, event_type: EstimateEventType
    ) -> EstimateMessage:
        return await self._session.send(
            "POST",
            f"estimates/{estimate_id}/messages",
            EstimateMessage,
            EstimateEvent(event_type=event_type),
        )

    async def mark_as_sent(self, estimate_id: int) -> EstimateMessage:
        return await self._event(estimate_id, EstimateEventType.SEND)

    async def mark_as_accepted(self, estimate_id: int) -> EstimateMessage:
        return await self._event(estimate_id, EstimateEventType.ACCEPT)

    async def mark_as_declined(self, estimate_id: int) -> EstimateMessage:
        return await self._event(estimate_id, EstimateEventType.DECLINE)

    async def reopen(self, estimate_id: int) -> EstimateMessage:
        return await self._event(estimate_id, EstimateEventType.RE_OPEN)


class EstimateItemCategories:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[EstimateItemCategory]:
        return self._session.paginate(
            "estimate_item_categories",
            "estimate_item_categories",
            EstimateItemCategory,
            params={"updated_since": updated_since},
        )

    async def get(self, category_id: int) -> EstimateItemCategory:
        return await self._session.get(
            f"estimate_item_categories/{category_id}", EstimateItemCategory
        )

    async def create(
        self, category: EstimateItemCategoryCreate
    ) -> EstimateItemCategory:
        return await self._session.send(
            "POST", "estimate_item_categories", EstimateItemCategory, category
        )

    async def update(
        self, category_id: int, changes: EstimateItemCategoryUpdate
    ) -> EstimateItemCategory:
        return await self._session.send(
            "PATCH",
            f"estimate_item_categories/{category_id}",
            EstimateItemCategory,
            changes,
        )

    async def delete(self, category_id: int) -> None:
        await self._session.delete(f"estimate_item_categories/{category_id}")
