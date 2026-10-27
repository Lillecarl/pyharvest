from __future__ import annotations

from enum import StrEnum

from pyharvest.models.base import HarvestInput, HarvestModel, Open


class WeekStartDay(StrEnum):
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"
    MONDAY = "Monday"


class TimeFormat(StrEnum):
    DECIMAL = "decimal"
    HOURS_MINUTES = "hours_minutes"


class Clock(StrEnum):
    H12 = "12h"
    H24 = "24h"


class CurrencyCodeDisplay(StrEnum):
    NONE = "iso_code_none"
    BEFORE = "iso_code_before"
    AFTER = "iso_code_after"


class CurrencySymbolDisplay(StrEnum):
    NONE = "symbol_none"
    BEFORE = "symbol_before"
    AFTER = "symbol_after"


class EInvoicingStatus(StrEnum):
    PENDING_KYB = "pending_kyb"
    KYB_FAILED = "kyb_failed"
    ACTIVE = "active"
    REJECTED = "rejected"


class Company(HarvestModel):
    base_uri: str
    full_domain: str
    name: str
    is_active: bool
    week_start_day: Open[WeekStartDay]
    wants_timestamp_timers: bool
    time_format: Open[TimeFormat]
    # A strftime pattern such as "%Y-%m-%d".
    date_format: str
    plan_type: str
    clock: Open[Clock]
    currency_code_display: Open[CurrencyCodeDisplay]
    currency_symbol_display: Open[CurrencySymbolDisplay]
    decimal_symbol: str
    thousands_separator: str
    color_scheme: str
    weekly_capacity: int
    """Seconds."""
    expense_feature: bool
    invoice_feature: bool
    estimate_feature: bool
    approval_feature: bool
    team_feature: bool
    e_invoicing_status: Open[EInvoicingStatus] | None = None
    # Undocumented; seen live.
    currency: str | None = None
    saml_sign_in_required: bool | None = None
    day_entry_notes_required: bool | None = None


class CompanyUpdate(HarvestInput):
    wants_timestamp_timers: bool | None = None
    weekly_capacity: int | None = None


class ReimbursementSettings(HarvestModel):
    expense_reimbursement_enabled: bool
    expense_reimbursement_approval_required: bool
    expense_reimbursement_decline_requests: bool


class ReimbursementSettingsUpdate(HarvestInput):
    """Harvest rejects ``null`` here with 422: leave a field unset to keep it."""

    expense_reimbursement_enabled: bool | None = None
    expense_reimbursement_approval_required: bool | None = None
    expense_reimbursement_decline_requests: bool | None = None


class EInvoicingProfile(HarvestInput):
    registered_name: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_postal_code: str | None = None
    address_country: str | None = None
    tax_id: str | None = None
    peppol_endpoint_id: str | None = None
    peppol_endpoint_scheme: str | None = None
    bank_account_number: str | None = None
    bank_account_routing_number: str | None = None
    bank_account_holder_name: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    company_registration_number: str | None = None
    legal_form: str | None = None
    payment_means_codes: list[str] | None = None


class EInvoicingEnrollment(HarvestInput):
    """``consent`` is the Peppol registration consent; Harvest refuses False."""

    contact_email: str
    consent: bool
    profile: EInvoicingProfile | None = None


class EInvoicingResult(HarvestModel):
    """``status`` is None once no enrollment exists."""

    status: Open[EInvoicingStatus] | None = None
