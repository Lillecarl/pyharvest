from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    first_name: str
    last_name: str
    email: str
