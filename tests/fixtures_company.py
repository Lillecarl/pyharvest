from __future__ import annotations

from typing import Any


def company(**overrides: Any) -> dict[str, Any]:
    return {
        "base_uri": "https://abc.harvestapp.com",
        "full_domain": "abc.harvestapp.com",
        "name": "ABC Corp",
        "is_active": True,
        "week_start_day": "Monday",
        "wants_timestamp_timers": False,
        "time_format": "decimal",
        "date_format": "%Y-%m-%d",
        "plan_type": "simple-v4",
        "expense_feature": True,
        "invoice_feature": True,
        "estimate_feature": False,
        "team_feature": False,
        "weekly_capacity": 144000,
        "approval_feature": True,
        "clock": "24h",
        "currency": "EUR",
        "currency_code_display": "iso_code_none",
        "currency_symbol_display": "symbol_before",
        "decimal_symbol": ".",
        "thousands_separator": ",",
        "color_scheme": "orange",
        "saml_sign_in_required": False,
        "day_entry_notes_required": False,
        "e_invoicing_status": None,
        **overrides,
    }


def reimbursement_settings(**overrides: Any) -> dict[str, Any]:
    return {
        "expense_reimbursement_enabled": True,
        "expense_reimbursement_approval_required": False,
        "expense_reimbursement_decline_requests": False,
        **overrides,
    }
