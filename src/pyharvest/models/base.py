from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# A documented closed set that Harvest may still extend: known values parse to
# the enum, new ones stay str instead of failing the whole record. Not a plain
# `E | str`: smart-mode unions pick str for every value.
type Open[E] = Annotated[E | str, Field(union_mode="left_to_right")]


class ApprovalStatus(StrEnum):
    """Approval state shared by time entries and expenses."""

    UNSUBMITTED = "unsubmitted"
    SUBMITTED = "submitted"
    APPROVED = "approved"


class HarvestModel(BaseModel):
    """A response record."""

    # extra="ignore": Harvest adds fields without notice, and an unknown field
    # must not break callers. tests/test_live.py catches fields the models miss.
    model_config = ConfigDict(frozen=True, extra="ignore")


class HarvestInput(BaseModel):
    """A request body. Only fields set explicitly are sent, so None clears."""

    # Aliases carry wire names pydantic cannot use as fields: `from` is a
    # keyword, and `_destroy` would be a private attribute.
    model_config = ConfigDict(
        extra="forbid", validate_by_name=True, serialize_by_alias=True
    )


class Ref(HarvestModel):
    """The ``{id, name}`` stub Harvest nests in place of a full object."""

    id: int
    name: str
