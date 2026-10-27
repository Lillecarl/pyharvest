from __future__ import annotations

import datetime as dt
import json
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.notifications import (
    Notification,
    NotificationCategory,
    NotificationChannel,
    NotificationChannelPreferenceInput,
    NotificationPreferencesUpdate,
    NotificationRemindersInput,
    NotificationToggleInput,
    NotificationType,
    NotificationWeekday,
)
from pyharvest.resources.notifications import NotificationPreferences, Notifications

from . import fixtures, fixtures_notifications

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_list_renders_filters(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("notifications").respond(
        json=fixtures.page(
            "notifications", [fixtures_notifications.notification()], None
        )
    )

    found = [
        n
        async for n in Notifications(harvest._session).list(
            updated_since=dt.datetime(2024, 3, 1, tzinfo=dt.UTC)
        )
    ]

    assert found[0].notification_type is NotificationType.TIMESHEET_SUBMITTED
    assert found[0].category is NotificationCategory.TIMESHEETS
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "updated_since": "2024-03-01T00:00:00Z",
    }


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("invoice_paid", NotificationType.INVOICE_PAID),
        ("brand_new_kind", "brand_new_kind"),
        (None, None),
    ],
)
def test_notification_type_is_open_and_nullable(
    raw: str | None, expected: object
) -> None:
    parsed = Notification.model_validate(
        fixtures_notifications.notification(notification_type=raw)
    ).notification_type

    assert parsed == expected
    assert type(parsed) is type(expected)


@pytest.mark.anyio
async def test_unread_count_and_peek(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("notifications/unread_count").respond(
        json=fixtures_notifications.unread_count()
    )
    router.get("notifications/peek").respond(
        json={
            "notifications": [fixtures_notifications.notification()],
            "unread_count": fixtures_notifications.unread_count(),
        }
    )
    resource = Notifications(harvest._session)

    count = await resource.unread_count()
    peek = await resource.peek()

    assert count.by_category == {"timesheets": 2, "timeoff": 1}
    assert peek.unread_count.total == 3
    assert peek.notifications[0].id == 900


@pytest.mark.anyio
async def test_mark_read_posts_without_body(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    one = router.post("notifications/900/mark_read").respond(
        json=fixtures_notifications.unread_count(total=2)
    )
    every = router.post("notifications/mark_all_read").respond(
        json={"total": 0, "by_category": {}}
    )
    resource = Notifications(harvest._session)

    assert (await resource.mark_read(900)).total == 2
    assert (await resource.mark_all_read()).by_category == {}
    assert one.calls.last.request.content == b""
    assert every.called


@pytest.mark.anyio
async def test_get_preferences(harvest: Harvest, router: respx.MockRouter) -> None:
    router.get("notification_preferences").respond(
        json=fixtures_notifications.notification_settings()
    )

    settings = await NotificationPreferences(harvest._session).get()

    assert settings.channels[0].channel is NotificationChannel.IN_APP
    assert settings.channels[1].feed_type is None
    assert settings.reminders.days[0] is NotificationWeekday.MONDAY


@pytest.mark.anyio
async def test_update_preferences_body(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.patch("notification_preferences").respond(
        json=fixtures_notifications.notification_settings()
    )

    await NotificationPreferences(harvest._session).update(
        NotificationPreferencesUpdate(
            channels=[
                NotificationChannelPreferenceInput(
                    notification_type="invoice_paid",
                    channel=NotificationChannel.EMAIL,
                    enabled=False,
                )
            ],
            weekly_report=NotificationToggleInput(enabled=False),
            reminders=NotificationRemindersInput(
                days=[NotificationWeekday.MONDAY], time_of_day=32400
            ),
        )
    )

    assert json.loads(route.calls.last.request.content) == {
        "channels": [
            {"notification_type": "invoice_paid", "channel": "email", "enabled": False}
        ],
        "weekly_report": {"enabled": False},
        "reminders": {"days": ["monday"], "time_of_day": 32400},
    }
