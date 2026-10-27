from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pyharvest.models.base import (
    ApprovalStatus,
    HarvestInput,
    HarvestModel,
    Open,
    Ref,
)
from pyharvest.models.projects import BudgetBy


class ProfitabilityGroupBy(StrEnum):
    PROJECT = "project"
    CLIENT = "client"
    TEAM = "team"
    TASK = "task"


class ProfitabilityProjectType(StrEnum):
    FIXED_FEE = "fixed_fee"
    TIME_AND_MATERIALS = "time_and_materials"
    NON_BILLABLE = "non_billable"


class ReturnOnCostUnbounded(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class DetailedTimeGroupBy(StrEnum):
    DATES = "dates"
    CLIENTS = "clients"
    PROJECTS = "projects"
    TASKS = "tasks"
    USERS = "users"


class DetailedExpenseGroupBy(StrEnum):
    DATES = "dates"
    CLIENTS = "clients"
    PROJECTS = "projects"
    CATEGORIES = "categories"
    USERS = "users"


class ReportSubject(StrEnum):
    EXPENSES = "expenses"
    INVOICES = "invoices"
    PAYMENTS = "payments"
    TIME = "time"


class GeneratedColumnType(StrEnum):
    TEXT = "text"
    NUMBER = "number"
    CURRENCY = "currency"
    DATE = "date"
    BOOL = "bool"
    TIME = "time"


class ExportFormat(StrEnum):
    CSV = "csv"
    XLSX = "xlsx"
    GDOC = "gdoc"
    IIF = "iif"
    PDF = "pdf"
    ZIP = "zip"


class ExportStatus(StrEnum):
    PENDING = "pending"
    COMPLETE = "complete"


class TimeReportResult(HarvestModel):
    total_hours: Decimal
    billable_hours: Decimal
    # Null for members, who lack "View billable rates and amounts".
    currency: str | None = None
    billable_amount: Decimal | None = None


class TimeByClient(TimeReportResult):
    client_id: int
    client_name: str


class TimeByProject(TimeReportResult):
    client_id: int
    client_name: str
    project_id: int
    project_name: str
    # Only with include_forecast=true on a Forecast-connected account.
    scheduled_hours: Decimal | None = None


class TimeByTask(TimeReportResult):
    task_id: int
    task_name: str


class TimeByUser(TimeReportResult):
    user_id: int
    user_name: str
    is_contractor: bool
    weekly_capacity: int
    """Seconds per week."""
    avatar_url: str
    scheduled_hours: Decimal | None = None


class ExpenseReportResult(HarvestModel):
    total_amount: Decimal
    billable_amount: Decimal
    currency: str


class ExpensesByClient(ExpenseReportResult):
    client_id: int
    client_name: str


class ExpensesByProject(ExpenseReportResult):
    client_id: int
    client_name: str
    project_id: int
    project_name: str


class ExpensesByCategory(ExpenseReportResult):
    expense_category_id: int
    expense_category_name: str


class ExpensesByUser(ExpenseReportResult):
    user_id: int
    user_name: str
    is_contractor: bool


class UninvoicedReportResult(HarvestModel):
    client_id: int
    client_name: str
    project_id: int
    project_name: str
    currency: str
    total_hours: Decimal
    uninvoiced_hours: Decimal
    uninvoiced_expenses: Decimal
    uninvoiced_amount: Decimal


class ProjectBudgetReportResult(HarvestModel):
    client_id: int
    client_name: str
    project_id: int
    project_name: str
    budget_is_monthly: bool
    budget_by: Open[BudgetBy]
    is_active: bool
    # Money budgets are hidden without "View billable rates and amounts".
    budget: Decimal | None = None
    budget_spent: Decimal | None = None
    budget_remaining: Decimal | None = None


class ProfitabilityResult(HarvestModel):
    """One row of the profitability report. Which subject fields are set
    depends on the grouping."""

    project_id: int | None = None
    project_name: str | None = None
    client_id: int | None = None
    client_name: str | None = None
    project_type: Open[ProfitabilityProjectType] | None = None
    user_id: int | None = None
    user_name: str | None = None
    task_id: int | None = None
    task_name: str | None = None
    is_active: bool
    currency: str
    missing_rates: bool
    missing_dates: bool
    total_revenue: Decimal
    total_cost: Decimal
    total_profit: Decimal
    invoiced_revenue: Decimal
    uninvoiced_revenue: Decimal
    # Null when cost is zero and profit is not; return_on_cost_unbounded
    # then gives the sign.
    return_on_cost: int | None = None
    return_on_cost_unbounded: Open[ReturnOnCostUnbounded] | None = None


class DetailedTimeRow(HarvestModel):
    id: int
    spent_date: dt.date
    hours: Decimal
    billable: bool
    is_billed: bool
    approval_status: Open[ApprovalStatus]
    notes: str | None = None
    client_id: int
    client_name: str
    project_id: int
    project_name: str
    task_id: int
    task_name: str
    user_id: int
    user_name: str


class DetailedExpenseRow(HarvestModel):
    id: int
    spent_date: dt.date
    total_cost: Decimal
    units: Decimal
    currency: str
    billable: bool
    is_billed: bool
    approval_status: Open[ApprovalStatus]
    notes: str | None = None
    client_id: int
    client_name: str
    project_id: int
    project_name: str
    expense_category_id: int
    expense_category_name: str
    user_id: int
    user_name: str


class SavedReport(HarvestModel):
    id: int
    name: str
    description: str | None = None
    # A plain dict, not a model: an update replaces the whole definition, so
    # callers send back what they read, and a model would drop unknown keys.
    # Any: arbitrary JSON from Harvest.
    configuration: dict[str, Any]
    lock_version: int
    owner: Ref
    is_owner: bool
    can_edit: bool
    created_at: dt.datetime
    updated_at: dt.datetime


class SavedReportCreate(HarvestInput):
    name: str
    configuration: dict[str, Any]
    description: str | None = None


class SavedReportUpdate(HarvestInput):
    """``configuration`` replaces the stored definition whole: send the full
    definition from a read, with edits."""

    name: str | None = None
    description: str | None = None
    configuration: dict[str, Any] | None = None
    lock_version: int | None = None


class ReportGenerate(HarvestInput):
    configuration: dict[str, Any]
    limit: int | None = None


class GeneratedReportColumn(HarvestModel):
    id: str
    label: str
    type: Open[GeneratedColumnType]


class GeneratedReport(HarvestModel):
    report_id: int | None = None
    subject: Open[ReportSubject]
    columns: list[GeneratedReportColumn]
    # Keyed by column ID, plus a zero-based "row" index.
    rows: list[dict[str, Any]]
    row_count: int
    overflow: bool
    # Only when money spans several currencies; parallel to rows.
    row_currencies: list[str] | None = None
    warnings: list[str]


class GeneratedReportEnvelope(HarvestModel):
    generated_report: GeneratedReport


class ReportExport(HarvestModel):
    id: int
    type: str
    format: Open[ExportFormat]
    status: Open[ExportStatus]
    created_at: dt.datetime
    completed_at: dt.datetime | None = None
    # Signed for one hour on each read; null while pending.
    download_url: str | None = None


class ReportExportCreate(HarvestInput):
    """``params`` holds the export's filters. Leave it unset for Harvest's
    default; an explicit None sends null, which Harvest refuses."""

    type: str
    export_format: ExportFormat
    params: dict[str, Any] | None = None
