from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.invoices import (
    EInvoiceSubmission,
    Invoice,
    InvoiceItemCategory,
    InvoiceMessage,
    InvoiceMessageCreate,
    InvoiceMessageEventType,
    InvoiceMessageTemplate,
    InvoicePayment,
)

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.invoices import (
        InvoiceCreate,
        InvoiceImportCreate,
        InvoiceItemCategoryCreate,
        InvoiceItemCategoryUpdate,
        InvoicePaymentCreate,
        InvoiceState,
        InvoiceUpdate,
    )


class Invoices:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        client_id: int | None = None,
        project_id: int | None = None,
        state: InvoiceState | None = None,
        updated_since: dt.datetime | None = None,
        from_: dt.date | None = None,
        to: dt.date | None = None,
    ) -> AsyncIterator[Invoice]:
        """``from_`` and ``to`` filter on ``issue_date``."""
        return self._session.paginate(
            "invoices",
            "invoices",
            Invoice,
            params={
                "client_id": client_id,
                "project_id": project_id,
                "state": state,
                "updated_since": updated_since,
                "from": from_,
                "to": to,
            },
        )

    async def get(self, invoice_id: int) -> Invoice:
        return await self._session.get(f"invoices/{invoice_id}", Invoice)

    async def create(self, invoice: InvoiceCreate | InvoiceImportCreate) -> Invoice:
        return await self._session.send("POST", "invoices", Invoice, invoice)

    async def update(self, invoice_id: int, changes: InvoiceUpdate) -> Invoice:
        """Line items in ``changes`` are added, changed or removed one by one;
        items not listed stay as they are."""
        return await self._session.send(
            "PATCH", f"invoices/{invoice_id}", Invoice, changes
        )

    async def delete(self, invoice_id: int) -> None:
        await self._session.delete(f"invoices/{invoice_id}")

    async def send_e_invoice(self, invoice_id: int) -> EInvoiceSubmission:
        """Send over Peppol. Beta endpoint."""
        return await self._session.send(
            "POST", f"invoices/{invoice_id}/send_e_invoice", EInvoiceSubmission
        )

    async def e_invoice_status(self, invoice_id: int) -> EInvoiceSubmission:
        """Beta endpoint."""
        return await self._session.get(
            f"invoices/{invoice_id}/e_invoice_status", EInvoiceSubmission
        )


class InvoiceMessages:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, invoice_id: int, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[InvoiceMessage]:
        return self._session.paginate(
            f"invoices/{invoice_id}/messages",
            "invoice_messages",
            InvoiceMessage,
            params={"updated_since": updated_since},
        )

    async def template(
        self,
        invoice_id: int,
        *,
        thank_you: bool | None = None,
        reminder: bool | None = None,
    ) -> InvoiceMessageTemplate:
        """The subject and body Harvest would use. Creates nothing."""
        return await self._session.get(
            f"invoices/{invoice_id}/messages/new",
            InvoiceMessageTemplate,
            params={"thank_you": thank_you, "reminder": reminder},
        )

    async def create(
        self, invoice_id: int, message: InvoiceMessageCreate
    ) -> InvoiceMessage:
        return await self._session.send(
            "POST", f"invoices/{invoice_id}/messages", InvoiceMessage, message
        )

    async def delete(self, invoice_id: int, message_id: int) -> None:
        await self._session.delete(f"invoices/{invoice_id}/messages/{message_id}")

    async def _event(
        self, invoice_id: int, event_type: InvoiceMessageEventType
    ) -> InvoiceMessage:
        return await self.create(
            invoice_id, InvoiceMessageCreate(event_type=event_type)
        )

    async def mark_sent(self, invoice_id: int) -> InvoiceMessage:
        """Mark a draft invoice as sent. Sends no email."""
        return await self._event(invoice_id, InvoiceMessageEventType.SEND)

    async def mark_closed(self, invoice_id: int) -> InvoiceMessage:
        """Write off an open invoice."""
        return await self._event(invoice_id, InvoiceMessageEventType.CLOSE)

    async def reopen(self, invoice_id: int) -> InvoiceMessage:
        """Re-open a closed invoice."""
        return await self._event(invoice_id, InvoiceMessageEventType.REOPEN)

    async def mark_draft(self, invoice_id: int) -> InvoiceMessage:
        """Return an open invoice to draft."""
        return await self._event(invoice_id, InvoiceMessageEventType.DRAFT)


class InvoicePayments:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, invoice_id: int, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[InvoicePayment]:
        return self._session.paginate(
            f"invoices/{invoice_id}/payments",
            "invoice_payments",
            InvoicePayment,
            params={"updated_since": updated_since},
        )

    async def create(
        self, invoice_id: int, payment: InvoicePaymentCreate
    ) -> InvoicePayment:
        return await self._session.send(
            "POST", f"invoices/{invoice_id}/payments", InvoicePayment, payment
        )

    async def delete(self, invoice_id: int, payment_id: int) -> None:
        await self._session.delete(f"invoices/{invoice_id}/payments/{payment_id}")


class InvoiceItemCategories:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[InvoiceItemCategory]:
        return self._session.paginate(
            "invoice_item_categories",
            "invoice_item_categories",
            InvoiceItemCategory,
            params={"updated_since": updated_since},
        )

    async def get(self, category_id: int) -> InvoiceItemCategory:
        return await self._session.get(
            f"invoice_item_categories/{category_id}", InvoiceItemCategory
        )

    async def create(self, category: InvoiceItemCategoryCreate) -> InvoiceItemCategory:
        return await self._session.send(
            "POST", "invoice_item_categories", InvoiceItemCategory, category
        )

    async def update(
        self, category_id: int, changes: InvoiceItemCategoryUpdate
    ) -> InvoiceItemCategory:
        return await self._session.send(
            "PATCH",
            f"invoice_item_categories/{category_id}",
            InvoiceItemCategory,
            changes,
        )

    async def delete(self, category_id: int) -> None:
        """Harvest refuses unless ``use_as_service`` and ``use_as_expense``
        are both false."""
        await self._session.delete(f"invoice_item_categories/{category_id}")
