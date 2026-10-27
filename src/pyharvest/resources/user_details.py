from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.user_details import (
    BillableRate,
    CostRate,
    ProjectAssignment,
    Teammate,
    Teammates,
)

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator, Sequence

    from pyharvest._session import Session
    from pyharvest.models.user_details import TeammatesUpdate, UserRateCreate


class UserTeammates:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self, user_id: int) -> AsyncIterator[Teammate]:
        return self._session.paginate(
            f"users/{user_id}/teammates", "teammates", Teammate
        )

    async def update(
        self, user_id: int, changes: TeammatesUpdate
    ) -> Sequence[Teammate]:
        response = await self._session.send(
            "PATCH", f"users/{user_id}/teammates", Teammates, changes
        )
        return response.teammates


class UserBillableRates:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self, user_id: int) -> AsyncIterator[BillableRate]:
        return self._session.paginate(
            f"users/{user_id}/billable_rates", "billable_rates", BillableRate
        )

    async def get(self, user_id: int, billable_rate_id: int) -> BillableRate:
        return await self._session.get(
            f"users/{user_id}/billable_rates/{billable_rate_id}", BillableRate
        )

    async def create(self, user_id: int, rate: UserRateCreate) -> BillableRate:
        return await self._session.send(
            "POST", f"users/{user_id}/billable_rates", BillableRate, rate
        )


class UserCostRates:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self, user_id: int) -> AsyncIterator[CostRate]:
        return self._session.paginate(
            f"users/{user_id}/cost_rates", "cost_rates", CostRate
        )

    async def get(self, user_id: int, cost_rate_id: int) -> CostRate:
        return await self._session.get(
            f"users/{user_id}/cost_rates/{cost_rate_id}", CostRate
        )

    async def create(self, user_id: int, rate: UserRateCreate) -> CostRate:
        return await self._session.send(
            "POST", f"users/{user_id}/cost_rates", CostRate, rate
        )


class UserProjectAssignments:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, user_id: int, *, updated_since: dt.datetime | None = None
    ) -> AsyncIterator[ProjectAssignment]:
        return self._session.paginate(
            f"users/{user_id}/project_assignments",
            "project_assignments",
            ProjectAssignment,
            params={"updated_since": updated_since},
        )

    def me(self) -> AsyncIterator[ProjectAssignment]:
        # A member gets 404 from users/{own id}/project_assignments; only
        # this path works for them.
        return self._session.paginate(
            "users/me/project_assignments", "project_assignments", ProjectAssignment
        )
