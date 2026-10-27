from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import StrEnum

from pydantic import ConfigDict, Field

from pyharvest.models.base import HarvestInput, HarvestModel, Open, Ref


class EstimateState(StrEnum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class EstimateEventType(StrEnum):
    SEND = "send"
    ACCEPT = "accept"
    DECLINE = "decline"
    RE_OPEN = "re-open"
    VIEW = "view"
    INVOICE = "invoice"


class EstimateLineItem(HarvestModel):
    id: int
    kind: str
    description: str | None = None
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    taxed: bool
    taxed2: bool


class Estimate(HarvestModel):
    id: int
    client: Ref
    line_items: list[EstimateLineItem]
    creator: Ref
    client_key: str
    number: str | None = None
    purchase_order: str | None = None
    amount: Decimal
    tax: Decimal | None = None
    tax_amount: Decimal | None = None
    tax2: Decimal | None = None
    tax2_amount: Decimal | None = None
    discount: Decimal | None = None
    discount_amount: Decimal | None = None
    subject: str | None = None
    notes: str | None = None
    currency: str
    state: Open[EstimateState]
    issue_date: dt.date | None = None
    sent_at: dt.datetime | None = None
    accepted_at: dt.datetime | None = None
    declined_at: dt.datetime | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class EstimateLineItemCreate(HarvestInput):
    kind: str
    unit_price: float
    description: str | None = None
    quantity: float | None = None
    taxed: bool | None = None
    taxed2: bool | None = None


class EstimateLineItemUpdate(HarvestInput):
    """Without ``id`` it adds a line item; with ``id`` it changes that one;
    ``destroy=True`` with ``id`` removes it."""

    # Harvest's key is "_destroy", which pydantic would take as a private attribute.
    model_config = ConfigDict(serialize_by_alias=True, validate_by_name=True)

    id: int | None = None
    kind: str | None = None
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    taxed: bool | None = None
    taxed2: bool | None = None
    destroy: bool | None = Field(default=None, alias="_destroy")


class EstimateCreate(HarvestInput):
    client_id: int
    number: str | None = None
    purchase_order: str | None = None
    tax: float | None = None
    tax2: float | None = None
    discount: float | None = None
    subject: str | None = None
    notes: str | None = None
    currency: str | None = None
    issue_date: dt.date | None = None
    line_items: list[EstimateLineItemCreate] | None = None


class EstimateUpdate(HarvestInput):
    client_id: int | None = None
    number: str | None = None
    purchase_order: str | None = None
    tax: float | None = None
    tax2: float | None = None
    discount: float | None = None
    subject: str | None = None
    notes: str | None = None
    currency: str | None = None
    issue_date: dt.date | None = None
    line_items: list[EstimateLineItemUpdate] | None = None


class EstimateMessageRecipient(HarvestModel):
    name: str | None = None
    email: str


class EstimateMessage(HarvestModel):
    id: int
    sent_by: str
    sent_by_email: str
    sent_from: str
    sent_from_email: str
    recipients: list[EstimateMessageRecipient]
    subject: str | None = None
    body: str | None = None
    send_me_a_copy: bool
    event_type: Open[EstimateEventType] | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class EstimateMessageRecipientInput(HarvestInput):
    email: str
    name: str | None = None


class EstimateMessageCreate(HarvestInput):
    """``event_type`` also runs that event against the estimate."""

    recipients: list[EstimateMessageRecipientInput]
    subject: str | None = None
    body: str | None = None
    send_me_a_copy: bool | None = None
    event_type: EstimateEventType | None = None


class EstimateEvent(HarvestInput):
    event_type: EstimateEventType


class EstimateItemCategory(HarvestModel):
    id: int
    name: str
    created_at: dt.datetime
    updated_at: dt.datetime


class EstimateItemCategoryCreate(HarvestInput):
    name: str


class EstimateItemCategoryUpdate(HarvestInput):
    name: str | None = None
