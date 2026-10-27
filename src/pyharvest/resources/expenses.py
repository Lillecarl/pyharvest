from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest.models.expenses import Expense, ExpenseCategory

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import AsyncIterator

    from pyharvest._session import Session
    from pyharvest.models.base import ApprovalStatus
    from pyharvest.models.expenses import (
        ExpenseCategoryCreate,
        ExpenseCategoryUpdate,
        ExpenseCreate,
        ExpenseUpdate,
    )


class Expenses:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        user_id: int | None = None,
        client_id: int | None = None,
        project_id: int | None = None,
        is_billed: bool | None = None,
        approval_status: ApprovalStatus | None = None,
        updated_since: dt.datetime | None = None,
        from_: dt.date | None = None,
        to: dt.date | None = None,
    ) -> AsyncIterator[Expense]:
        return self._session.paginate(
            "expenses",
            "expenses",
            Expense,
            params={
                "user_id": user_id,
                "client_id": client_id,
                "project_id": project_id,
                "is_billed": is_billed,
                "approval_status": approval_status,
                "updated_since": updated_since,
                "from": from_,
                "to": to,
            },
        )

    async def get(self, expense_id: int) -> Expense:
        return await self._session.get(f"expenses/{expense_id}", Expense)

    async def create(self, expense: ExpenseCreate) -> Expense:
        return await self._session.send("POST", "expenses", Expense, expense)

    async def update(self, expense_id: int, changes: ExpenseUpdate) -> Expense:
        return await self._session.send(
            "PATCH", f"expenses/{expense_id}", Expense, changes
        )

    async def delete(self, expense_id: int) -> None:
        await self._session.delete(f"expenses/{expense_id}")

    async def approve(self, expense_id: int) -> Expense:
        """Beta endpoint. Also approves the submitter's time entries on the
        same project and day."""
        return await self._session.send(
            "POST", f"expenses/{expense_id}/approve", Expense
        )

    async def withdraw(self, expense_id: int) -> Expense:
        """Beta endpoint. Also withdraws the submitter's time entries on the
        same project and day."""
        return await self._session.send(
            "POST", f"expenses/{expense_id}/withdraw", Expense
        )


class ExpenseCategories:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        is_active: bool | None = None,
        updated_since: dt.datetime | None = None,
    ) -> AsyncIterator[ExpenseCategory]:
        return self._session.paginate(
            "expense_categories",
            "expense_categories",
            ExpenseCategory,
            params={"is_active": is_active, "updated_since": updated_since},
        )

    async def get(self, category_id: int) -> ExpenseCategory:
        return await self._session.get(
            f"expense_categories/{category_id}", ExpenseCategory
        )

    async def create(self, category: ExpenseCategoryCreate) -> ExpenseCategory:
        return await self._session.send(
            "POST", "expense_categories", ExpenseCategory, category
        )

    async def update(
        self, category_id: int, changes: ExpenseCategoryUpdate
    ) -> ExpenseCategory:
        return await self._session.send(
            "PATCH", f"expense_categories/{category_id}", ExpenseCategory, changes
        )

    async def delete(self, category_id: int) -> None:
        await self._session.delete(f"expense_categories/{category_id}")
