from __future__ import annotations

import datetime as dt
import json
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.roles import CustomRoleCreate, CustomRoleUpdate, RoleCreate
from pyharvest.resources.roles import CustomRoles, Permissions, Roles

from . import fixtures, fixtures_roles

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_roles_list(harvest: Harvest, router: respx.MockRouter) -> None:
    router.get("roles").respond(
        json=fixtures.page("roles", [fixtures_roles.role()], None)
    )

    roles = [r async for r in Roles(harvest._session).list()]

    assert roles[0].user_ids == [1, 7]


@pytest.mark.anyio
async def test_role_create_sends_only_set_fields(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("roles").respond(201, json=fixtures_roles.role())

    await Roles(harvest._session).create(RoleCreate(name="Designer"))

    assert json.loads(route.calls.last.request.content) == {"name": "Designer"}


@pytest.mark.anyio
async def test_role_delete(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.delete("roles/40").respond(200)

    await Roles(harvest._session).delete(40)

    assert route.called


@pytest.mark.anyio
async def test_custom_roles_list_renders_filter(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.get("custom_roles").respond(
        json=fixtures.page("custom_roles", [fixtures_roles.custom_role()], None)
    )

    roles = [
        r
        async for r in CustomRoles(harvest._session).list(
            updated_since=dt.datetime(2024, 3, 1, tzinfo=dt.UTC)
        )
    ]

    assert roles[0].permission_ids == [3, 7, 12]
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "updated_since": "2024-03-01T00:00:00Z",
    }


@pytest.mark.anyio
async def test_custom_role_create_and_update(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    create = router.post("custom_roles").respond(201, json=fixtures_roles.custom_role())
    update = router.patch("custom_roles/50").respond(json=fixtures_roles.custom_role())
    custom_roles = CustomRoles(harvest._session)

    await custom_roles.create(CustomRoleCreate(name="Team Lead", permission_ids=[3]))
    await custom_roles.update(50, CustomRoleUpdate(permission_ids=[3, 7]))

    assert json.loads(create.calls.last.request.content) == {
        "name": "Team Lead",
        "permission_ids": [3],
    }
    assert json.loads(update.calls.last.request.content) == {"permission_ids": [3, 7]}


@pytest.mark.anyio
async def test_custom_role_delete_returns_record(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.delete("custom_roles/50").respond(json=fixtures_roles.custom_role())

    deleted = await CustomRoles(harvest._session).delete(50)

    assert deleted.id == 50


@pytest.mark.anyio
async def test_permissions_list(harvest: Harvest, router: respx.MockRouter) -> None:
    router.get("permissions").respond(
        json=fixtures.page("permissions", [fixtures_roles.permission()], None)
    )

    permissions = [p async for p in Permissions(harvest._session).list()]

    assert permissions[0].name == "timers:write:own"
