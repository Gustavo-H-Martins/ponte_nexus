from decimal import Decimal

from sqlalchemy import select

from src.models.db_models import BudgetModel
from src.repositories.base import BaseRepository


class BudgetRepository(BaseRepository):
    def get_by_category_and_month(
        self, category_id: int, year_month: str
    ) -> BudgetModel | None:
        stmt = select(BudgetModel).where(
            BudgetModel.category_id == category_id,
            BudgetModel.year_month == year_month,
        )
        return self.session.scalar(stmt)

    def list_by_month(self, year_month: str) -> list[BudgetModel]:
        stmt = select(BudgetModel).where(BudgetModel.year_month == year_month)
        return list(self.session.scalars(stmt))

    def upsert(
        self, category_id: int, year_month: str, limit_amount: Decimal
    ) -> BudgetModel:
        """Cria ou atualiza o orçamento de uma categoria para o mês informado."""
        existing = self.get_by_category_and_month(category_id, year_month)
        if existing:
            existing.limit_amount = limit_amount
            self.session.flush()
            return existing
        budget = BudgetModel(
            category_id=category_id,
            year_month=year_month,
            limit_amount=limit_amount,
        )
        self.session.add(budget)
        self.session.flush()
        return budget

    def delete_by_id(self, budget_id: int) -> None:
        budget = self.session.get(BudgetModel, budget_id)
        if budget:
            self.session.delete(budget)
            self.session.flush()
