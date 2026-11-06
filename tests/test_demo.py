"""Write tests against a Harvest trial account.

Opt-in: `pytest -m demo`. Credentials come from `.demoenv` in the repository
root, or the file `HARVEST_ENV_FILE` names; never from the environment, which
direnv fills with the real account. The `demo` fixture refuses any company
whose plan is not a trial. Each test deletes what it creates.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from pyharvest import Harvest
from pyharvest.client import read_env_file
from pyharvest.models.clients import ClientCreate

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

pytestmark = [pytest.mark.anyio, pytest.mark.demo]

ENV_FILE = Path(
    os.environ.get("HARVEST_ENV_FILE", Path(__file__).parent.parent / ".demoenv")
)
PREFIX = "pyharvest-test"


@pytest.fixture
async def demo() -> AsyncIterator[Harvest]:
    if not ENV_FILE.is_file():
        pytest.skip(f"no {ENV_FILE}")
    env = read_env_file(ENV_FILE)
    async with Harvest(
        access_token=env["HARVEST_TOKEN"],
        account_id=env["HARVEST_ACCOUNT"],
        user_agent="pyharvest demo tests",
    ) as harvest:
        company = await harvest.company.get()
        if company.plan_type != "trial":
            pytest.fail(f"{ENV_FILE} is {company.name!r}, plan {company.plan_type!r}")
        yield harvest


def name(kind: str) -> str:
    """A unique name a leftover record can be found and removed by."""
    return f"{PREFIX} {kind} {uuid.uuid4().hex[:8]}"


async def test_client_round_trip(demo: Harvest) -> None:
    created = await demo.clients.create(ClientCreate(name=name("client")))
    try:
        assert (await demo.clients.get(created.id)).name == created.name
    finally:
        await demo.clients.delete(created.id)
