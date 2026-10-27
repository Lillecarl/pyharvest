from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.reports import (
    DetailedExpenseRow,
    DetailedTimeRow,
    ExpensesByCategory,
    ExpensesByClient,
    ExpensesByProject,
    ExpensesByUser,
    GeneratedReportEnvelope,
    ProfitabilityResult,
    ProjectBudgetReportResult,
    ReportExport,
    SavedReport,
    TimeByClient,
    TimeByProject,
    TimeByTask,
    TimeByUser,
    UninvoicedReportResult,
)

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.base import ApprovalStatus
    from pyharvest.models.reports import (
        DetailedExpenseGroupBy,
        DetailedTimeGroupBy,
        GeneratedReport,
        ProfitabilityGroupBy,
        ReportExportCreate,
        ReportGenerate,
        SavedReportCreate,
        SavedReportUpdate,
    )


class Reports:
    """The Reports API. Harvest limits it to 100 requests per 15 minutes.

    Report dates go out as ISO ``YYYY-MM-DD``; Harvest also accepts the
    ``YYYYMMDD`` form its older examples show. A timeframe spans at most
    365 days.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # Time reports

    def time_clients(
        self, *, from_: dt.date, to: dt.date, include_fixed_fee: bool | None = None
    ) -> AsyncIterator[TimeByClient]:
        return self._session.paginate(
            "reports/time/clients",
            "results",
            TimeByClient,
            params={"from": from_, "to": to, "include_fixed_fee": include_fixed_fee},
        )

    def time_projects(
        self,
        *,
        from_: dt.date,
        to: dt.date,
        include_fixed_fee: bool | None = None,
        include_forecast: bool | None = None,
    ) -> AsyncIterator[TimeByProject]:
        return self._session.paginate(
            "reports/time/projects",
            "results",
            TimeByProject,
            params={
                "from": from_,
                "to": to,
                "include_fixed_fee": include_fixed_fee,
                "include_forecast": include_forecast,
            },
        )

    def time_tasks(
        self, *, from_: dt.date, to: dt.date, include_fixed_fee: bool | None = None
    ) -> AsyncIterator[TimeByTask]:
        return self._session.paginate(
            "reports/time/tasks",
            "results",
            TimeByTask,
            params={"from": from_, "to": to, "include_fixed_fee": include_fixed_fee},
        )

    def time_team(
        self,
        *,
        from_: dt.date,
        to: dt.date,
        include_fixed_fee: bool | None = None,
        include_forecast: bool | None = None,
    ) -> AsyncIterator[TimeByUser]:
        return self._session.paginate(
            "reports/time/team",
            "results",
            TimeByUser,
            params={
                "from": from_,
                "to": to,
                "include_fixed_fee": include_fixed_fee,
                "include_forecast": include_forecast,
            },
        )

    def time_detailed(
        self,
        *,
        from_: dt.date,
        to: dt.date,
        client_id: int | None = None,
        project_id: int | None = None,
        task_id: int | None = None,
        user_id: int | None = None,
        is_billed: bool | None = None,
        approval_status: ApprovalStatus | None = None,
        group_by: DetailedTimeGroupBy | None = None,
    ) -> AsyncIterator[DetailedTimeRow]:
        """Entry-level rows. The response's ``totals`` are not returned."""
        return self._session.paginate(
            "reports/time/detailed",
            "results",
            DetailedTimeRow,
            params={
                "from": from_,
                "to": to,
                "client_id": client_id,
                "project_id": project_id,
                "task_id": task_id,
                "user_id": user_id,
                "is_billed": is_billed,
                "approval_status": approval_status,
                "group_by": group_by,
            },
        )

    # Expense reports

    def expenses_clients(
        self, *, from_: dt.date, to: dt.date
    ) -> AsyncIterator[ExpensesByClient]:
        return self._session.paginate(
            "reports/expenses/clients",
            "results",
            ExpensesByClient,
            params={"from": from_, "to": to},
        )

    def expenses_projects(
        self, *, from_: dt.date, to: dt.date
    ) -> AsyncIterator[ExpensesByProject]:
        return self._session.paginate(
            "reports/expenses/projects",
            "results",
            ExpensesByProject,
            params={"from": from_, "to": to},
        )

    def expenses_categories(
        self, *, from_: dt.date, to: dt.date
    ) -> AsyncIterator[ExpensesByCategory]:
        return self._session.paginate(
            "reports/expenses/categories",
            "results",
            ExpensesByCategory,
            params={"from": from_, "to": to},
        )

    def expenses_team(
        self, *, from_: dt.date, to: dt.date
    ) -> AsyncIterator[ExpensesByUser]:
        return self._session.paginate(
            "reports/expenses/team",
            "results",
            ExpensesByUser,
            params={"from": from_, "to": to},
        )

    def expenses_detailed(
        self,
        *,
        from_: dt.date,
        to: dt.date,
        client_id: int | None = None,
        project_id: int | None = None,
        expense_category_id: int | None = None,
        user_id: int | None = None,
        is_billed: bool | None = None,
        approval_status: ApprovalStatus | None = None,
        group_by: DetailedExpenseGroupBy | None = None,
    ) -> AsyncIterator[DetailedExpenseRow]:
        """Expense-level rows. The response's ``totals`` are not returned."""
        return self._session.paginate(
            "reports/expenses/detailed",
            "results",
            DetailedExpenseRow,
            params={
                "from": from_,
                "to": to,
                "client_id": client_id,
                "project_id": project_id,
                "expense_category_id": expense_category_id,
                "user_id": user_id,
                "is_billed": is_billed,
                "approval_status": approval_status,
                "group_by": group_by,
            },
        )

    # Other reports

    def uninvoiced(
        self, *, from_: dt.date, to: dt.date, include_fixed_fee: bool | None = None
    ) -> AsyncIterator[UninvoicedReportResult]:
        return self._session.paginate(
            "reports/uninvoiced",
            "results",
            UninvoicedReportResult,
            params={"from": from_, "to": to, "include_fixed_fee": include_fixed_fee},
        )

    def project_budget(
        self, *, is_active: bool | None = None
    ) -> AsyncIterator[ProjectBudgetReportResult]:
        return self._session.paginate(
            "reports/project_budget",
            "results",
            ProjectBudgetReportResult,
            params={"is_active": is_active},
        )

    def profitability(
        self,
        *,
        from_: dt.date,
        to: dt.date,
        group_by: ProfitabilityGroupBy | None = None,
        client_id: int | None = None,
        project_id: int | None = None,
    ) -> AsyncIterator[ProfitabilityResult]:
        return self._session.paginate(
            "reports/profitability",
            "results",
            ProfitabilityResult,
            params={
                "from": from_,
                "to": to,
                "group_by": group_by,
                "client_id": client_id,
                "project_id": project_id,
            },
        )

    # Saved and generated reports

    def saved_list(
        self, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[SavedReport]:
        return self._session.paginate(
            "reports/saved",
            "saved_reports",
            SavedReport,
            params={"updated_since": updated_since},
        )

    async def saved_get(self, saved_report_id: int) -> SavedReport:
        return await self._session.get(f"reports/saved/{saved_report_id}", SavedReport)

    async def saved_create(self, report: SavedReportCreate) -> SavedReport:
        return await self._session.send("POST", "reports/saved", SavedReport, report)

    async def saved_update(
        self, saved_report_id: int, changes: SavedReportUpdate
    ) -> SavedReport:
        return await self._session.send(
            "PATCH", f"reports/saved/{saved_report_id}", SavedReport, changes
        )

    async def saved_delete(self, saved_report_id: int) -> SavedReport:
        """Return the deleted report, as Harvest does."""
        return await self._session.send(
            "DELETE", f"reports/saved/{saved_report_id}", SavedReport
        )

    async def generate(self, definition: ReportGenerate) -> GeneratedReport:
        envelope = await self._session.send(
            "POST", "reports/generate", GeneratedReportEnvelope, definition
        )
        return envelope.generated_report

    async def run_saved(
        self, saved_report_id: int, *, limit: int | None = None
    ) -> GeneratedReport:
        envelope = await self._session.get(
            f"reports/generated/{saved_report_id}",
            GeneratedReportEnvelope,
            params={"limit": limit},
        )
        return envelope.generated_report

    # Exports

    async def export_create(self, export: ReportExportCreate) -> ReportExport:
        return await self._session.send("POST", "reports/exports", ReportExport, export)

    async def export_get(self, export_id: int) -> ReportExport:
        return await self._session.get(f"reports/exports/{export_id}", ReportExport)

    async def export_download(self, export_id: int) -> bytes:
        """The finished file (CSV, XLSX, PDF, ZIP, ...). Poll ``export_get``
        until ``status`` is complete first; earlier, Harvest answers 409."""
        response = await self._session.request(
            "GET", f"reports/exports/{export_id}/download"
        )
        # The client does not follow redirects, so a redirect would give an
        # empty body that looks like an empty file.
        if response.status_code != 200:
            raise RuntimeError(
                f"export {export_id}: download answered {response.status_code}"
            )
        return response.content
