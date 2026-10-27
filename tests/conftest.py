from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx

from pyharvest import BASE_URL, Harvest

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def router() -> Iterator[respx.MockRouter]:
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        yield router


@pytest.fixture
async def harvest(router: respx.MockRouter) -> AsyncIterator[Harvest]:
    async with Harvest(
        access_token="tok",
        account_id="42",
        user_agent="pyharvest-tests (ada@example.com)",
    ) as harvest:
        yield harvest
