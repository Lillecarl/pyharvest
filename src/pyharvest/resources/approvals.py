from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.approvals import Approval, ApprovalSubmission

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.approvals import ApprovalBucket, ApprovalSubmit


class Approvals:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        period_start: dt.date,
        period_end: dt.date,
        *,
        approval_status: ApprovalBucket | None = None,
        user_id: int | None = None,
    ) -> AsyncIterator[Approval]:
        """Both period bounds are inclusive; the period spans at most 366 days."""
        return self._session.paginate(
            "approvals",
            "approvals",
            Approval,
            params={
                "period_start": period_start,
                "period_end": period_end,
                "approval_status": approval_status,
                "user_id": user_id,
            },
        )

    async def submit(self, timesheet: ApprovalSubmit) -> ApprovalSubmission:
        """Not idempotent: a repeat notifies approvers again. After a timeout,
        read the period back with ``list`` before retrying."""
        return await self._session.send(
            "POST", "approvals/submit", ApprovalSubmission, timesheet
        )
