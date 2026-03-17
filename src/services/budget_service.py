import logging
from decimal import Decimal

import pandas as pd

from src.config.database import SessionLocal
from src.models.db_models import CategoryModel
from src.repositories.budget_repository import BudgetRepository

logger = logging.getLogger(__name__)


class BudgetService:
    """Gerencia metas de gasto mensais por categoria."""

    def __init__(self, session_factory=SessionLocal, owner_id: int | None = None) -> None:
        self.session_factory = session_factory
        self.owner_id = owner_id

    def set_budget(
        self, category_id: int, year_month: str, limit_amount: Decimal
    ) -> None:
        """Define ou atualiza o limite de gasto de uma categoria no mês informado."""
        with self.session_factory() as session:
            BudgetRepository(session, self.owner_id).upsert(category_id, year_month, limit_amount)
            session.commit()
        logger.info("Orçamento definido: categoria=%d mês=%s limite=%s", category_id, year_month, limit_amount)

    def get_utilization(self, df: pd.DataFrame, year_month: str) -> list[dict]:
        """Retorna utilização do orçamento por categoria para o período informado.

        Cada item contém: category, limit, spent, pct, status (ok/warning/danger).
        """
        with self.session_factory() as session:
            budgets = BudgetRepository(session, self.owner_id).list_by_month(year_month)
            if not budgets:
                return []

            # Resolve nomes de categorias e monta mapeamento id → nome
            cat_names: dict[int, str] = {}
            for budget in budgets:
                cat = session.get(CategoryModel, budget.category_id)
                cat_names[budget.category_id] = cat.name if cat else str(budget.category_id)

            # Filtra despesas do período no DataFrame
            expense_mask = (
                (df["transaction_type"] == "despesa")
                & (df["date"].dt.to_period("M").astype(str) == year_month)
            ) if not df.empty else pd.Series([], dtype=bool)

            expense_df = df[expense_mask].copy() if not df.empty else pd.DataFrame()

            result: list[dict] = []
            for budget in budgets:
                cat_name = cat_names[budget.category_id]
                spent = 0.0
                if not expense_df.empty:
                    spent = float(expense_df[expense_df["category"] == cat_name]["amount"].sum())

                limit = float(budget.limit_amount)
                pct = (spent / limit * 100) if limit > 0 else 0.0
                result.append({
                    "category": cat_name,
                    "limit": limit,
                    "spent": spent,
                    "pct": round(pct, 1),
                    "status": "danger" if pct >= 90 else "warning" if pct >= 70 else "ok",
                })

        return sorted(result, key=lambda x: x["pct"], reverse=True)
