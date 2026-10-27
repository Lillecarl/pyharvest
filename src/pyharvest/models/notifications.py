from __future__ import annotations

import datetime as dt
from enum import StrEnum

from pyharvest.models.base import HarvestInput, HarvestModel, Open


class NotificationType(StrEnum):
    TIMESHEET_SUBMITTED = "timesheet_submitted"
    TIMESHEET_APPROVED = "timesheet_approved"
    TIMESHEET_LOCKING = "timesheet_locking"
    TIME_TRACKING_REMINDER = "time_tracking_reminder"
    INVOICE_PAID = "invoice_paid"
    PTO_REQUEST = "pto_request"
    PTO_REVIEWED = "pto_reviewed"
    PTO_CANCELLED = "pto_cancelled"
    EXPENSE_REQUEST = "expense_request"
    FORECAST_ACCESS_REQUEST = "forecast_access_request"
    HARVEST_SEAT_REQUEST = "harvest_seat_request"
    BULK_ACTION_COMPLETED = "bulk_action_completed"


class NotificationCategory(StrEnum):
    TIMESHEETS = "timesheets"
    INVOICES = "invoices"
    TIMEOFF = "timeoff"
    EXPENSES = "expenses"
    ACCOUNT = "account"


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"


class NotificationWeekday(StrEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Notification(HarvestModel):
    id: int
    notification_type: Open[NotificationType] | None = None
    """None for retired types."""
    category: Open[NotificationCategory]
    occurred_at: dt.datetime
    read_at: dt.datetime | None = None
    updated_at: dt.datetime
    title: str
    summary: str | None = None


class NotificationUnreadCount(HarvestModel):
    total: int
    # Categories with no unread notifications are absent.
    by_category: dict[str, int]


class NotificationPeek(HarvestModel):
    notifications: list[Notification]
    unread_count: NotificationUnreadCount


class NotificationChannelPreference(HarvestModel):
    # Preference types are finer than feed types: timesheet_submitted_person,
    # occasional_updates, project_deleted.
    notification_type: str
    channel: Open[NotificationChannel]
    enabled: bool
    feed_type: Open[NotificationType] | None = None
    category: Open[NotificationCategory] | None = None


class NotificationToggle(HarvestModel):
    enabled: bool


class NotificationReminders(HarvestModel):
    enabled: bool
    time_of_day: int
    """Seconds after local midnight in the user's timezone."""
    days: list[Open[NotificationWeekday]]
    via_desktop: bool
    via_slack: bool
    team_wide: bool


class NotificationSettings(HarvestModel):
    """The notification preference object."""

    channels: list[NotificationChannelPreference]
    weekly_report: NotificationToggle
    approval_confirmation: NotificationToggle
    reminders: NotificationReminders


class NotificationChannelPreferenceInput(HarvestInput):
    notification_type: str
    channel: NotificationChannel
    enabled: bool


class NotificationToggleInput(HarvestInput):
    enabled: bool


class NotificationRemindersInput(HarvestInput):
    """Harvest refuses null here, so leave a field unset to keep it."""

    enabled: bool | None = None
    time_of_day: int | None = None
    days: list[NotificationWeekday] | None = None
    via_desktop: bool | None = None
    via_slack: bool | None = None
    team_wide: bool | None = None


class NotificationPreferencesUpdate(HarvestInput):
    """Omitted keys keep their value. Harvest refuses null for every key."""

    channels: list[NotificationChannelPreferenceInput] | None = None
    weekly_report: NotificationToggleInput | None = None
    approval_confirmation: NotificationToggleInput | None = None
    reminders: NotificationRemindersInput | None = None
