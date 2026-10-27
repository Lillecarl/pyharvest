from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pyharvest.models.base import HarvestModel


class User(HarvestModel):
    id: int
    first_name: str
    last_name: str
    email: str
    telephone: str | None = None
    timezone: str
    weekly_capacity: int
    """Seconds of availability per week."""
    has_access_to_all_future_projects: bool
    is_contractor: bool
    is_active: bool
    employee_id: str | None = None
    calendar_integration_enabled: bool | None = None
    calendar_integration_source: str | None = None
    can_create_projects: bool | None = None
    roles: list[str]
    access_roles: list[str]
    permissions_profile: str | None = None
    permissions_claims: list[str] | None = None
    avatar_url: str | None = None
    # Hidden from members: present only for managers and administrators.
    saml_exempt: bool | None = None
    default_hourly_rate: Decimal | None = None
    cost_rate: Decimal | None = None
    created_at: dt.datetime
    updated_at: dt.datetime
