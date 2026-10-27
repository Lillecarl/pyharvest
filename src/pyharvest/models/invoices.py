from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum

from pydantic import AwareDatetime, ConfigDict, Field

from pyharvest.models.base import HarvestInput, HarvestModel, Open, Ref


class InvoiceState(StrEnum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    CLOSED = "closed"


class PaymentTerm(StrEnum):
    UPON_RECEIPT = "upon receipt"
    NET_15 = "net 15"
    NET_30 = "net 30"
    NET_45 = "net 45"
    NET_60 = "net 60"
    CUSTOM = "custom"


class PaymentOption(StrEnum):
    ACH = "ach"
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"


class TimeSummaryType(StrEnum):
    PROJECT = "project"
    TASK = "task"
    PEOPLE = "people"
    DETAILED = "detailed"


class ExpenseSummaryType(StrEnum):
    PROJECT = "project"
    CATEGORY = "category"
    PEOPLE = "people"
    DETAILED = "detailed"


class InvoiceMessageEventType(StrEnum):
    SEND = "send"
    CLOSE = "close"
    REOPEN = "re-open"
    DRAFT = "draft"


class _AliasedInput(HarvestInput):
    # `from` is a keyword and `_destroy` a private name in pydantic, so both
    # fields need an alias, and send() dumps without by_alias.
    model_config = ConfigDict(
        extra="forbid", validate_by_name=True, serialize_by_alias=True
    )


class InvoiceLineItemProject(Ref):
    code: str | None = None


class InvoiceLineItem(HarvestModel):
    id: int
    project: InvoiceLineItemProject | None = None
    # The name of an invoice item category, which the account defines.
    kind: str
    description: str | None = None
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    taxed: bool
    taxed2: bool


class InvoiceEstimate(HarvestModel):
    id: int


class InvoiceRetainer(HarvestModel):
    id: int


class Invoice(HarvestModel):
    id: int
    client: Ref
    line_items: list[InvoiceLineItem]
    estimate: InvoiceEstimate | None = None
    retainer: InvoiceRetainer | None = None
    creator: Ref | None = None
    client_key: str
    number: str
    purchase_order: str | None = None
    amount: Decimal
    due_amount: Decimal
    tax: Decimal | None = None
    # Documented as null when no tax is set; the examples show 0.0.
    tax_amount: Decimal | None = None
    tax2: Decimal | None = None
    tax2_amount: Decimal | None = None
    discount: Decimal | None = None
    discount_amount: Decimal | None = None
    subject: str | None = None
    notes: str | None = None
    currency: str
    state: Open[InvoiceState]
    period_start: dt.date | None = None
    period_end: dt.date | None = None
    issue_date: dt.date
    due_date: dt.date | None = None
    payment_term: Open[PaymentTerm] | None = None
    # Missing from some documented responses.
    payment_options: list[Open[PaymentOption]] | None = None
    sent_at: dt.datetime | None = None
    paid_at: dt.datetime | None = None
    paid_date: dt.date | None = None
    closed_at: dt.datetime | None = None
    recurring_invoice_id: int | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class InvoiceLineItemCreate(HarvestInput):
    kind: str
    unit_price: float
    project_id: int | None = None
    description: str | None = None
    quantity: float | None = None
    taxed: bool | None = None
    taxed2: bool | None = None


class InvoiceLineItemUpdate(_AliasedInput):
    """Without ``id`` Harvest adds a line item; with ``id`` it changes that
    item, and ``destroy=True`` removes it."""

    id: int | None = None
    destroy: bool | None = Field(default=None, alias="_destroy")
    project_id: int | None = None
    kind: str | None = None
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    taxed: bool | None = None
    taxed2: bool | None = None


class InvoiceTimeImport(_AliasedInput):
    """Leave out ``from_`` and ``to`` to import all unbilled time."""

    summary_type: TimeSummaryType
    from_: dt.date | None = Field(default=None, alias="from")
    to: dt.date | None = None


class InvoiceExpenseImport(_AliasedInput):
    """Leave out ``from_`` and ``to`` to import all unbilled expenses."""

    summary_type: ExpenseSummaryType
    from_: dt.date | None = Field(default=None, alias="from")
    to: dt.date | None = None
    attach_receipts: bool | None = None


class InvoiceLineItemsImport(HarvestInput):
    project_ids: list[int]
    time: InvoiceTimeImport | None = None
    expenses: InvoiceExpenseImport | None = None


class _InvoiceCreateFields(HarvestInput):
    client_id: int
    estimate_id: int | None = None
    number: str | None = None
    purchase_order: str | None = None
    tax: float | None = None
    tax2: float | None = None
    discount: float | None = None
    subject: str | None = None
    notes: str | None = None
    currency: str | None = None
    issue_date: dt.date | None = None
    # Harvest ignores due_date unless payment_term is custom.
    due_date: dt.date | None = None
    payment_term: PaymentTerm | None = None
    payment_options: list[PaymentOption] | None = None


class InvoiceCreate(_InvoiceCreateFields):
    """A free-form invoice: the line items are given here."""

    retainer_id: int | None = None
    line_items: list[InvoiceLineItemCreate] | None = None


class InvoiceImportCreate(_InvoiceCreateFields):
    """An invoice whose line items Harvest builds from tracked time and
    expenses."""

    line_items_import: InvoiceLineItemsImport


class InvoiceUpdate(HarvestInput):
    client_id: int | None = None
    retainer_id: int | None = None
    estimate_id: int | None = None
    number: str | None = None
    purchase_order: str | None = None
    tax: float | None = None
    tax2: float | None = None
    discount: float | None = None
    subject: str | None = None
    notes: str | None = None
    currency: str | None = None
    issue_date: dt.date | None = None
    due_date: dt.date | None = None
    payment_term: PaymentTerm | None = None
    payment_options: list[PaymentOption] | None = None
    line_items: list[InvoiceLineItemUpdate] | None = None


class EInvoiceSubmission(HarvestModel):
    """Peppol readiness and the latest submission. A beta endpoint: Harvest
    may still change the shape."""

    # Open-ended, many values; null when the invoice was never submitted.
    status: str | None = None
    submitted_at: dt.datetime | None = None
    last_event_at: dt.datetime | None = None
    document_id: str | None = None
    failure_reason: str | None = None
    eligible: bool
    blocked_reason: str | None = None


class InvoiceMessageRecipient(HarvestModel):
    name: str | None = None
    email: str


class InvoiceMessage(HarvestModel):
    id: int
    sent_by: str | None = None
    sent_by_email: str | None = None
    sent_from: str | None = None
    sent_from_email: str | None = None
    recipients: list[InvoiceMessageRecipient]
    subject: str | None = None
    body: str | None = None
    include_link_to_client_invoice: bool | None = None
    """Deprecated by Harvest: true when the invoice has payment options."""
    attach_pdf: bool
    send_me_a_copy: bool
    thank_you: bool
    # Null for a message that was sent by email.
    event_type: Open[InvoiceMessageEventType] | None = None
    reminder: bool
    send_reminder_on: dt.date | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class InvoiceMessageTemplate(HarvestModel):
    """The configured subject and body for a new message; nothing is sent."""

    invoice_id: int
    subject: str
    body: str
    reminder: bool
    thank_you: bool


class InvoiceMessageRecipientInput(HarvestInput):
    email: str
    name: str | None = None


class InvoiceMessageCreate(HarvestInput):
    """Leave ``event_type`` unset to send the message by email. It then needs
    ``recipients`` or ``send_me_a_copy=True``, or Harvest rejects it."""

    recipients: list[InvoiceMessageRecipientInput] | None = None
    subject: str | None = None
    body: str | None = None
    include_link_to_client_invoice: bool | None = None
    """Deprecated by Harvest: False clears the invoice's payment options."""
    attach_pdf: bool | None = None
    send_me_a_copy: bool | None = None
    thank_you: bool | None = None
    event_type: InvoiceMessageEventType | None = None


class PaymentGateway(HarvestModel):
    # Both null for a payment recorded by hand.
    id: int | None = None
    name: str | None = None


class InvoicePayment(HarvestModel):
    id: int
    amount: Decimal
    paid_at: dt.datetime | None = None
    paid_date: dt.date | None = None
    recorded_by: str | None = None
    recorded_by_email: str | None = None
    notes: str | None = None
    transaction_id: str | None = None
    payment_gateway: PaymentGateway | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class InvoicePaymentCreate(HarvestInput):
    """Set ``paid_at`` or ``paid_date``, not both."""

    amount: float
    paid_at: AwareDatetime | None = None
    paid_date: dt.date | None = None
    notes: str | None = None
    send_thank_you: bool | None = None


class InvoiceItemCategory(HarvestModel):
    id: int
    name: str
    use_as_service: bool
    use_as_expense: bool
    created_at: dt.datetime
    updated_at: dt.datetime


class InvoiceItemCategoryCreate(HarvestInput):
    name: str


class InvoiceItemCategoryUpdate(HarvestInput):
    name: str | None = None
