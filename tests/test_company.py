from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.company import (
    Clock,
    CompanyUpdate,
    EInvoicingEnrollment,
    EInvoicingProfile,
    EInvoicingStatus,
    ReimbursementSettingsUpdate,
    WeekStartDay,
)
from pyharvest.resources.company import CompanySettings

from . import fixtures_company

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_get(harvest: Harvest, router: respx.MockRouter) -> None:
    router.get("company").respond(json=fixtures_company.company())

    company = await CompanySettings(harvest._session).get()

    assert company.week_start_day is WeekStartDay.MONDAY
    assert company.clock is Clock.H24
    assert company.e_invoicing_status is None


@pytest.mark.anyio
async def test_update_body(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.patch("company").respond(
        json=fixtures_company.company(weekly_capacity=126000)
    )

    company = await CompanySettings(harvest._session).update(
        CompanyUpdate(weekly_capacity=126000)
    )

    assert company.weekly_capacity == 126000
    assert json.loads(route.calls.last.request.content) == {"weekly_capacity": 126000}


@pytest.mark.anyio
async def test_reimbursement_settings(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    router.get("company/reimbursement_settings").respond(
        json=fixtures_company.reimbursement_settings()
    )
    route = router.patch("company/reimbursement_settings").respond(
        json=fixtures_company.reimbursement_settings(
            expense_reimbursement_enabled=False
        )
    )
    company = CompanySettings(harvest._session)

    assert (await company.reimbursement_settings()).expense_reimbursement_enabled
    updated = await company.update_reimbursement_settings(
        ReimbursementSettingsUpdate(expense_reimbursement_enabled=False)
    )

    assert not updated.expense_reimbursement_enabled
    assert json.loads(route.calls.last.request.content) == {
        "expense_reimbursement_enabled": False
    }


@pytest.mark.anyio
async def test_enroll_e_invoicing(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("company/e_invoicing").respond(
        201, json={"status": "pending_kyb"}
    )

    result = await CompanySettings(harvest._session).enroll_e_invoicing(
        EInvoicingEnrollment(
            contact_email="billing@example.com",
            consent=True,
            profile=EInvoicingProfile(
                registered_name="ABC Corp B.V.", payment_means_codes=["30"]
            ),
        )
    )

    assert result.status is EInvoicingStatus.PENDING_KYB
    assert json.loads(route.calls.last.request.content) == {
        "contact_email": "billing@example.com",
        "consent": True,
        "profile": {"registered_name": "ABC Corp B.V.", "payment_means_codes": ["30"]},
    }


@pytest.mark.anyio
async def test_disconnect_e_invoicing(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.delete("company/e_invoicing").respond(json={"status": None})

    result = await CompanySettings(harvest._session).disconnect_e_invoicing()

    assert result.status is None
    assert route.called
