from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class HarvestModel(BaseModel):
    # extra="ignore": Harvest adds fields without notice, and an unknown field
    # must not break callers. tests/live catches fields the models miss.
    model_config = ConfigDict(frozen=True, extra="ignore")


class Ref(HarvestModel):
    """The ``{id, name}`` stub Harvest nests in place of a full object."""

    id: int
    name: str
