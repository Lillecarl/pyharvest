from __future__ import annotations

from typing import TYPE_CHECKING

from pyharvest._session import Attachment
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


def _receipt(receipt: Attachment | None) -> dict[str, Attachment] | None:
    return None if receipt is None else {"receipt": receipt}


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

    async def download_receipt(self, expense_id: int) -> Attachment | None:
        """The receipt attached to an expense, or None when it has none."""
        receipt = (await self.get(expense_id)).receipt
        if receipt is None:
            return None
        response = await self._session.download(receipt.url)
        return Attachment(
            receipt.file_name,
            response.content,
            receipt.content_type
            or response.headers.get("Content-Type", "application/octet-stream"),
        )

    async def create(
        self, expense: ExpenseCreate, *, receipt: Attachment | None = None
    ) -> Expense:
        """A receipt makes the request multipart, which cannot send null."""
        return await self._session.send(
            "POST", "expenses", Expense, expense, files=_receipt(receipt)
        )

    async def update(
        self,
        expense_id: int,
        changes: ExpenseUpdate,
        *,
        receipt: Attachment | None = None,
    ) -> Expense:
        """A receipt replaces the attached one, and cannot be sent with a null."""
        return await self._session.send(
            "PATCH",
            f"expenses/{expense_id}",
            Expense,
            changes,
            files=_receipt(receipt),
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
