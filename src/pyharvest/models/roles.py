from __future__ import annotations

import datetime as dt

from pyharvest.models.base import HarvestInput, HarvestModel


class Role(HarvestModel):
    """A descriptive label on users, unrelated to ``CustomRole`` permissions."""

    id: int
    name: str
    user_ids: list[int]
    created_at: dt.datetime
    updated_at: dt.datetime


class RoleCreate(HarvestInput):
    name: str
    user_ids: list[int] | None = None


class RoleUpdate(HarvestInput):
    name: str | None = None
    # Replaces the whole set.
    user_ids: list[int] | None = None


class CustomRole(HarvestModel):
    """A custom permissions profile, assigned through ``custom_role_id``."""

    id: int
    name: str
    permission_ids: list[int]
    created_at: dt.datetime
    updated_at: dt.datetime


class CustomRoleCreate(HarvestInput):
    name: str
    permission_ids: list[int]


class CustomRoleUpdate(HarvestInput):
    name: str | None = None
    # Replaces the whole set; Harvest rejects null and [].
    permission_ids: list[int] | None = None


class Permission(HarvestModel):
    id: int
    name: str
    """The ``resource:action:scope`` claim, as in ``User.permissions_claims``."""
    label: str
    created_at: dt.datetime
    updated_at: dt.datetime
