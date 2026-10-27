from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.company import Company, EInvoicingResult, ReimbursementSettings

if TYPE_CHECKING:
    from pyharvest._session import Session
    from pyharvest.models.company import (
        CompanyUpdate,
        EInvoicingEnrollment,
        ReimbursementSettingsUpdate,
    )


class CompanySettings:
    """The account's company: a singleton, so no list, create or delete."""

    def __init__(self, session: Session) -> None:
        self._session = session

    async def get(self) -> Company:
        return await self._session.get("company", Company)

    async def update(self, changes: CompanyUpdate) -> Company:
        return await self._session.send("PATCH", "company", Company, changes)

    async def reimbursement_settings(self) -> ReimbursementSettings:
        return await self._session.get(
            "company/reimbursement_settings", ReimbursementSettings
        )

    async def update_reimbursement_settings(
        self, changes: ReimbursementSettingsUpdate
    ) -> ReimbursementSettings:
        return await self._session.send(
            "PATCH", "company/reimbursement_settings", ReimbursementSettings, changes
        )

    async def enroll_e_invoicing(
        self, enrollment: EInvoicingEnrollment
    ) -> EInvoicingResult:
        return await self._session.send(
            "POST", "company/e_invoicing", EInvoicingResult, enrollment
        )

    async def disconnect_e_invoicing(self) -> EInvoicingResult:
        return await self._session.send(
            "DELETE", "company/e_invoicing", EInvoicingResult
        )
