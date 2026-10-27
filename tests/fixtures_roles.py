from __future__ import annotations

from typing import Any


def role(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 40,
        "name": "Designer",
        "user_ids": [1, 7],
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def custom_role(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 50,
        "name": "Team Lead",
        "permission_ids": [3, 7, 12],
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }


def permission(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 3,
        "name": "timers:write:own",
        "label": "Log and edit their own time",
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        **overrides,
    }
