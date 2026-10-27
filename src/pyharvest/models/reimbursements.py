from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum

from pyharvest.models.base import HarvestInput, HarvestModel, Open, Ref


class ReimbursementQueue(StrEnum):
    READY = "ready"
    REIMBURSED = "reimbursed"
    REJECTED = "rejected"


class ReimbursementPayoutStatus(StrEnum):
    READY = "ready"
    WAITING_FOR_ACH = "waiting_for_ach"
    SETUP_NEEDED = "setup_needed"


class ReimbursementExpenseCategory(Ref):
    unit_name: str | None = None


class Reimbursement(HarvestModel):
    id: int
    """The ID of the backing expense."""
    status: Open[ReimbursementQueue]
    approval_status: str
    payout_ready: bool
    payout_status: Open[ReimbursementPayoutStatus]
    reimbursement_status: str | None = None
    paid_on: dt.date | None = None
    fee: Decimal | None = None
    """Payout-level fee in USD, repeated on every row of the payout."""
    reference: str | None = None
    """Stripe PaymentIntent ID."""
    usd_amount: Decimal | None = None
    rejected_reason: str | None = None
    spent_date: dt.date
    total_cost: Decimal
    currency_code: str
    notes: str | None = None
    billable: bool
    user: Ref
    client: Ref
    project: Ref
    expense_category: ReimbursementExpenseCategory


class ReimbursementReject(HarvestInput):
    reason: str
    """Up to 255 characters; Harvest emails it to the member."""
