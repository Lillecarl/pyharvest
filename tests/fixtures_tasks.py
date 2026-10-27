from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses. Any: raw JSON
# bodies handed to respx.


def task(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 4,
        "name": "Programming",
        "billable_by_default": True,
        "default_hourly_rate": 100.0,
        "is_default": True,
        "is_active": True,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }
