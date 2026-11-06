from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx

from pyharvest import Harvest, NotFoundError, UnauthorizedError
from pyharvest.client import read_env_file

from . import fixtures

if TYPE_CHECKING:
    from pathlib import Path


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


def test_from_env_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HARVEST_ENV_FILE", raising=False)
    monkeypatch.setenv("HARVEST_TOKEN", "env-tok")
    monkeypatch.setenv("HARVEST_ACCOUNT", "1")

    headers = Harvest.from_env(user_agent="t")._session.http.headers

    assert (headers["Authorization"], headers["Harvest-Account-Id"]) == (
        "Bearer env-tok",
        "1",
    )


def test_env_file_wins_over_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env_file = tmp_path / ".demoenv"
    env_file.write_text(
        "# demo\n\nexport HARVEST_TOKEN='file-tok'\nHARVEST_ACCOUNT = \"2\"\n"
    )
    monkeypatch.setenv("HARVEST_TOKEN", "env-tok")
    monkeypatch.setenv("HARVEST_ACCOUNT", "1")
    monkeypatch.setenv("HARVEST_ENV_FILE", str(env_file))

    headers = Harvest.from_env(user_agent="t")._session.http.headers

    assert (headers["Authorization"], headers["Harvest-Account-Id"]) == (
        "Bearer file-tok",
        "2",
    )


def test_env_file_never_falls_back_to_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env_file = tmp_path / ".demoenv"
    env_file.write_text("HARVEST_TOKEN=file-tok\n")
    monkeypatch.setenv("HARVEST_ACCOUNT", "1")
    monkeypatch.setenv("HARVEST_ENV_FILE", str(env_file))

    with pytest.raises(KeyError, match="HARVEST_ACCOUNT"):
        Harvest.from_env(user_agent="t")


def test_env_file_error_hides_the_line(tmp_path: Path) -> None:
    env_file = tmp_path / ".demoenv"
    env_file.write_text("secret-token-without-key\n")

    with pytest.raises(ValueError, match=r":1: not KEY=VALUE") as caught:
        read_env_file(env_file)
    assert "secret" not in str(caught.value)
