from __future__ import annotations

import datetime as dt
from enum import StrEnum

from pyharvest.models.base import HarvestInput, HarvestModel, Open, Ref


class InvoiceRecipientStatus(StrEnum):
    NONE = "none"
    RECIPIENT = "recipient"
    CC = "cc"
    BCC = "bcc"


class Client(HarvestModel):
    id: int
    name: str
    is_active: bool
    address: str | None = None
    statement_key: str
    currency: str
    created_at: dt.datetime
    updated_at: dt.datetime


class ClientCreate(HarvestInput):
    """``currency`` defaults to the company's currency."""

    name: str
    is_active: bool | None = None
    address: str | None = None
    currency: str | None = None


class ClientUpdate(HarvestInput):
    name: str | None = None
    is_active: bool | None = None
    address: str | None = None
    currency: str | None = None


class Contact(HarvestModel):
    id: int
    client: Ref
    title: str | None = None
    first_name: str
    last_name: str | None = None
    email: str | None = None
    phone_office: str | None = None
    phone_mobile: str | None = None
    fax: str | None = None
    # Documented, but absent from the documented example responses.
    invoice_recipient_status: Open[InvoiceRecipientStatus] | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class ContactCreate(HarvestInput):
    client_id: int
    first_name: str
    title: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_office: str | None = None
    phone_mobile: str | None = None
    fax: str | None = None
    invoice_recipient_status: InvoiceRecipientStatus | None = None


class ContactUpdate(HarvestInput):
    client_id: int | None = None
    first_name: str | None = None
    title: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_office: str | None = None
    phone_mobile: str | None = None
    fax: str | None = None
    invoice_recipient_status: InvoiceRecipientStatus | None = None
