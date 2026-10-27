from __future__ import annotations

from typing import Any

# Synthetic records shaped like the documented responses. Any: raw JSON bodies.


def import_run(**overrides: Any) -> dict[str, Any]:
    return {
        "id": 600,
        "import_type": "project",
        "status": "completed",
        "csv_file_name": "projects.csv",
        "imported_rows_count": 12,
        "imported_hours": 0.0,
        "error_rows_count": 1,
        "csv_errors_available": True,
        "created_at": "2024-03-01T09:00:00Z",
        "updated_at": "2024-03-01T09:02:00Z",
        "started_at": "2024-03-01T09:00:05Z",
        "completed_at": "2024-03-01T09:02:00Z",
        "reverted_at": None,
        **overrides,
    }
