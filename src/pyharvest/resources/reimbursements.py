from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.reimbursements import Reimbursement, ReimbursementReject

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.reimbursements import ReimbursementQueue


class Reimbursements:
    def __init__(self, session: Session) -> None:
        self._session = session

    # No updated_since: Harvest answers it with 422 on this endpoint.
    def list(
        self,
        *,
        status: ReimbursementQueue | None = None,
        project_id: int | None = None,
        user_id: int | None = None,
        from_: dt.date | None = None,
        to: dt.date | None = None,
    ) -> AsyncIterator[Reimbursement]:
        """``status`` defaults to ``ready`` on Harvest's side."""
        return self._session.paginate(
            "reimbursements",
            "reimbursements",
            Reimbursement,
            params={
                "status": status,
                "project_id": project_id,
                "user_id": user_id,
                "from": from_,
                "to": to,
            },
        )

    async def reject(self, reimbursement_id: int, reason: str) -> Reimbursement:
        return await self._session.send(
            "POST",
            f"reimbursements/{reimbursement_id}/reject",
            Reimbursement,
            ReimbursementReject(reason=reason),
        )

    async def restore(self, reimbursement_id: int) -> Reimbursement:
        return await self._session.send(
            "POST", f"reimbursements/{reimbursement_id}/restore", Reimbursement
        )
