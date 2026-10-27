from __future__ import annotations

import os
from typing import TYPE_CHECKING, Final, Self

import httpx

from pyharvest._session import Session
from pyharvest.resources import (
    Approvals,
    Clients,
    CompanySettings,
    Contacts,
    CustomRoles,
    EstimateItemCategories,
    EstimateMessages,
    Estimates,
    ExpenseCategories,
    Expenses,
    GustoIntegration,
    GustoSyncRuns,
    HolidayCalendarEntries,
    HolidayCalendars,
    Imports,
    InvoiceItemCategories,
    InvoiceMessages,
    InvoicePayments,
    Invoices,
    NotificationPreferences,
    Notifications,
    Permissions,
    Projects,
    PtoAllocations,
    PtoAssignments,
    Reimbursements,
    Reports,
    Roles,
    Tags,
    TaskAssignments,
    Tasks,
    TimeEntries,
    TimeOffBalances,
    TimeOffPolicies,
    TimeOffRequests,
    UserAssignments,
    UserBillableRates,
    UserCostRates,
    UserProjectAssignments,
    Users,
    UserTeammates,
    WorkSchedules,
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
        self.approvals: Final = Approvals(self._session)
        self.clients: Final = Clients(self._session)
        self.company: Final = CompanySettings(self._session)
        self.contacts: Final = Contacts(self._session)
        self.custom_roles: Final = CustomRoles(self._session)
        self.estimate_item_categories: Final = EstimateItemCategories(self._session)
        self.estimate_messages: Final = EstimateMessages(self._session)
        self.estimates: Final = Estimates(self._session)
        self.expense_categories: Final = ExpenseCategories(self._session)
        self.expenses: Final = Expenses(self._session)
        self.gusto: Final = GustoIntegration(self._session)
        self.gusto_sync_runs: Final = GustoSyncRuns(self._session)
        self.holiday_calendar_entries: Final = HolidayCalendarEntries(self._session)
        self.holiday_calendars: Final = HolidayCalendars(self._session)
        self.imports: Final = Imports(self._session)
        self.invoice_item_categories: Final = InvoiceItemCategories(self._session)
        self.invoice_messages: Final = InvoiceMessages(self._session)
        self.invoice_payments: Final = InvoicePayments(self._session)
        self.invoices: Final = Invoices(self._session)
        self.notification_preferences: Final = NotificationPreferences(self._session)
        self.notifications: Final = Notifications(self._session)
        self.permissions: Final = Permissions(self._session)
        self.projects: Final = Projects(self._session)
        self.pto_allocations: Final = PtoAllocations(self._session)
        self.pto_assignments: Final = PtoAssignments(self._session)
        self.reimbursements: Final = Reimbursements(self._session)
        self.reports: Final = Reports(self._session)
        self.roles: Final = Roles(self._session)
        self.tags: Final = Tags(self._session)
        self.task_assignments: Final = TaskAssignments(self._session)
        self.tasks: Final = Tasks(self._session)
        self.time_entries: Final = TimeEntries(self._session)
        self.time_off_balances: Final = TimeOffBalances(self._session)
        self.time_off_policies: Final = TimeOffPolicies(self._session)
        self.time_off_requests: Final = TimeOffRequests(self._session)
        self.user_assignments: Final = UserAssignments(self._session)
        self.user_billable_rates: Final = UserBillableRates(self._session)
        self.user_cost_rates: Final = UserCostRates(self._session)
        self.user_project_assignments: Final = UserProjectAssignments(self._session)
        self.user_teammates: Final = UserTeammates(self._session)
        self.users: Final = Users(self._session)
        self.work_schedules: Final = WorkSchedules(self._session)

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
