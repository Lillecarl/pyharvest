from __future__ import annotations

import os
from typing import TYPE_CHECKING, Final, Self

import httpx

from pyharvest._session import Session
from pyharvest.resources import (
    Clients,
    CompanySettings,
    Contacts,
    CustomRoles,
    EstimateItemCategories,
    EstimateMessages,
    Estimates,
    ExpenseCategories,
    Expenses,
    InvoiceItemCategories,
    InvoiceMessages,
    InvoicePayments,
    Invoices,
    Permissions,
    Projects,
    Reports,
    Roles,
    Tags,
    TaskAssignments,
    Tasks,
    TimeEntries,
    UserAssignments,
    UserBillableRates,
    UserCostRates,
    UserProjectAssignments,
    Users,
    UserTeammates,
)

if TYPE_CHECKING:
    from types import TracebackType

BASE_URL: Final = "https://api.harvestapp.com/v2/"


class Harvest:
    """Async client for the Harvest API v2.

    Harvest requires a User-Agent that names the application and a contact,
    for example ``"MyApp (me@example.com)"``.
    """

    def __init__(
        self,
        *,
        access_token: str,
        account_id: str,
        user_agent: str,
        base_url: str = BASE_URL,
        max_retries: int = 3,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        http = httpx.AsyncClient(
            base_url=base_url,
            # httpx's 5s default is short for a 2000-record page; a live run
            # timed out on it.
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Harvest-Account-Id": account_id,
                "User-Agent": user_agent,
            },
            transport=transport,
        )
        self._session = Session(http, max_retries=max_retries)
        self.clients: Final = Clients(self._session)
        self.company: Final = CompanySettings(self._session)
        self.contacts: Final = Contacts(self._session)
        self.custom_roles: Final = CustomRoles(self._session)
        self.estimate_item_categories: Final = EstimateItemCategories(self._session)
        self.estimate_messages: Final = EstimateMessages(self._session)
        self.estimates: Final = Estimates(self._session)
        self.expense_categories: Final = ExpenseCategories(self._session)
        self.expenses: Final = Expenses(self._session)
        self.invoice_item_categories: Final = InvoiceItemCategories(self._session)
        self.invoice_messages: Final = InvoiceMessages(self._session)
        self.invoice_payments: Final = InvoicePayments(self._session)
        self.invoices: Final = Invoices(self._session)
        self.permissions: Final = Permissions(self._session)
        self.projects: Final = Projects(self._session)
        self.reports: Final = Reports(self._session)
        self.roles: Final = Roles(self._session)
        self.tags: Final = Tags(self._session)
        self.task_assignments: Final = TaskAssignments(self._session)
        self.tasks: Final = Tasks(self._session)
        self.time_entries: Final = TimeEntries(self._session)
        self.user_assignments: Final = UserAssignments(self._session)
        self.user_billable_rates: Final = UserBillableRates(self._session)
        self.user_cost_rates: Final = UserCostRates(self._session)
        self.user_project_assignments: Final = UserProjectAssignments(self._session)
        self.user_teammates: Final = UserTeammates(self._session)
        self.users: Final = Users(self._session)

    @classmethod
    def from_env(cls, *, user_agent: str) -> Self:
        """Read ``HARVEST_TOKEN`` and ``HARVEST_ACCOUNT`` from the environment."""
        return cls(
            access_token=os.environ["HARVEST_TOKEN"],
            account_id=os.environ["HARVEST_ACCOUNT"],
            user_agent=user_agent,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._session.http.aclose()
