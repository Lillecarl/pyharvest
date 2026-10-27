from __future__ import annotations

import httpx
import pytest
import respx

from pyharvest import BASE_URL, Harvest, User


@pytest.mark.anyio
async def test_me_sends_auth_headers() -> None:
    with respx.mock(base_url=BASE_URL) as router:
        route = router.get("users/me").respond(
            json={
                "id": 1,
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
            }
        )
        async with Harvest(
            access_token="tok",
            account_id="42",
            user_agent="pyharvest-tests (ada@example.com)",
        ) as harvest:
            user = await harvest.me()

    assert user == User(
        id=1, first_name="Ada", last_name="Lovelace", email="ada@example.com"
    )
    request: httpx.Request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer tok"
    assert request.headers["Harvest-Account-Id"] == "42"
    assert request.headers["User-Agent"] == "pyharvest-tests (ada@example.com)"
