from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pyharvest.models.base import (
    ApprovalStatus,
    HarvestInput,
    HarvestModel,
    Open,
    Ref,
)


class ExpenseClient(Ref):
    currency: str | None = None


class ExpenseProject(Ref):
    code: str | None = None


class ExpenseCategoryRef(Ref):
    unit_name: str | None = None
    unit_price: Decimal | None = None


class ExpenseReceipt(HarvestModel):
    url: str
    file_name: str
    file_size: int | None = None
    content_type: str | None = None


class ExpenseInvoice(HarvestModel):
    id: int
    number: str


class ExpenseUserAssignment(HarvestModel):
    id: int
    is_project_manager: bool
    is_active: bool
    use_default_rates: bool | None = None
    budget: Decimal | None = None
    hourly_rate: Decimal | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class Expense(HarvestModel):
    id: int
    client: ExpenseClient
    project: ExpenseProject
    expense_category: ExpenseCategoryRef
    user: Ref
    user_assignment: ExpenseUserAssignment | None = None
    receipt: ExpenseReceipt | None = None
    invoice: ExpenseInvoice | None = None
    notes: str | None = None
    # Documented as integer; live values are floats (mileage, for one).
    units: Decimal
    total_cost: Decimal
    billable: bool
    is_closed: bool
    """Deprecated by Harvest: read ``approval_status``."""
    approval_status: Open[ApprovalStatus]
    is_locked: bool
    is_explicitly_locked: bool | None = None
    is_billed: bool
    locked_reason: str | None = None
    reimbursement: bool | None = None
    spent_date: dt.date
    created_at: dt.datetime
    updated_at: dt.datetime


class ExpenseCreate(HarvestInput):
    """Pass ``units`` for a unit-based expense category, ``total_cost``
    otherwise. Receipt uploads need multipart and are not supported."""

    project_id: int
    expense_category_id: int
    spent_date: dt.date
    user_id: int | None = None
    units: float | None = None
    total_cost: float | None = None
    notes: str | None = None
    billable: bool | None = None


class ExpenseUpdate(HarvestInput):
    """Harvest drops ``project_id`` and ``expense_category_id`` silently on a
    locked expense."""

    project_id: int | None = None
    expense_category_id: int | None = None
    spent_date: dt.date | None = None
    units: float | None = None
    total_cost: float | None = None
    notes: str | None = None
    billable: bool | None = None
    delete_receipt: bool | None = None


class ExpenseCategory(HarvestModel):
    id: int
    name: str
    unit_name: str | None = None
    unit_price: Decimal | None = None
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime


class ExpenseCategoryCreate(HarvestInput):
    name: str
    unit_name: str | None = None
    unit_price: float | None = None
    is_active: bool | None = None


class ExpenseCategoryUpdate(HarvestInput):
    name: str | None = None
    unit_name: str | None = None
    unit_price: float | None = None
    is_active: bool | None = None
