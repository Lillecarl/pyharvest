from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.notifications import (
    Notification,
    NotificationPeek,
    NotificationSettings,
    NotificationUnreadCount,
)

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.notifications import NotificationPreferencesUpdate


class Notifications:
    """The authenticated user's own notification feed."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[Notification]:
        return self._session.paginate(
            "notifications",
            "notifications",
            Notification,
            params={"updated_since": updated_since},
        )

    async def unread_count(self) -> NotificationUnreadCount:
        return await self._session.get(
            "notifications/unread_count", NotificationUnreadCount
        )

    async def peek(self) -> NotificationPeek:
        """The six newest notifications and the unread count."""
        return await self._session.get("notifications/peek", NotificationPeek)

    async def mark_read(self, notification_id: int) -> NotificationUnreadCount:
        return await self._session.send(
            "POST",
            f"notifications/{notification_id}/mark_read",
            NotificationUnreadCount,
        )

    async def mark_all_read(self) -> NotificationUnreadCount:
        return await self._session.send(
            "POST", "notifications/mark_all_read", NotificationUnreadCount
        )


class NotificationPreferences:
    """The authenticated user's own notification preferences."""

    def __init__(self, session: Session) -> None:
        self._session = session

    async def get(self) -> NotificationSettings:
        return await self._session.get("notification_preferences", NotificationSettings)

    async def update(
        self, changes: NotificationPreferencesUpdate
    ) -> NotificationSettings:
        return await self._session.send(
            "PATCH", "notification_preferences", NotificationSettings, changes
        )
