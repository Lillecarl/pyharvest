from __future__ import annotations

import pytest
import respx

from pyharvest import Harvest, NotFoundError, UnauthorizedError

from . import fixtures


@pytest.mark.anyio
async def test_me_sends_auth_headers(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.get("users/me").respond(json=fixtures.user())

    user = await harvest.users.me()

    assert (user.id, user.email) == (1, "ada@example.com")
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer tok"
    assert request.headers["Harvest-Account-Id"] == "42"
    assert request.headers["User-Agent"] == "pyharvest-tests (ada@example.com)"


@pytest.mark.anyio
async def test_list_follows_next_link(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    next_url = "https://api.harvestapp.com/v2/users?cursor=abc&per_page=2000"
    first = router.get("users", params={"is_active": "true"}).respond(
        json=fixtures.page("users", [fixtures.user(id=1)], next_url)
    )
    second = router.get("users", params={"cursor": "abc"}).respond(
        json=fixtures.page("users", [fixtures.user(id=2)], None)
    )

    users = [u.id async for u in harvest.users.list(is_active=True)]

    assert users == [1, 2]
    assert first.calls.last.request.url.params["per_page"] == "2000"
    second_params = second.calls.last.request.url.params
    assert "is_active" not in second_params
    assert second_params["cursor"] == "abc"


@pytest.mark.anyio
async def test_retries_after_429(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.get("users/me")
    route.side_effect = [
        respx.MockResponse(429, headers={"Retry-After": "0"}),
        respx.MockResponse(200, json=fixtures.user()),
    ]

    await harvest.users.me()

    assert route.call_count == 2


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("status", "payload", "error", "message"),
    [
        (
            401,
            {"error": "invalid_token", "error_description": "token is bad"},
            UnauthorizedError,
            "token is bad",
        ),
        (404, {"status": 404, "error": "Not Found"}, NotFoundError, "Not Found"),
    ],
)
async def test_error_mapping(
    harvest: Harvest,
    router: respx.MockRouter,
    status: int,
    payload: dict[str, object],
    error: type[Exception],
    message: str,
) -> None:
    router.get("users/me").respond(status, json=payload)

    with pytest.raises(error) as info:
        await harvest.users.me()

    assert getattr(info.value, "message", None) == message
