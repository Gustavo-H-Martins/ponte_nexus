import pandas as pd
from sqlalchemy import text

from src.fin_dashboard.core.database import engine


def load_transactions() -> pd.DataFrame:
    query = text(
        """
        SELECT
            id, source, occurred_on, description, category, tx_type, amount, account
        FROM transactions
        ORDER BY occurred_on DESC, id DESC
        """
    )
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def kpis(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {"incomes": 0.0, "expenses": 0.0, "net": 0.0}
    incomes = float(df.loc[df["tx_type"] == "income", "amount"].sum())
    expenses = float(df.loc[df["tx_type"] == "expense", "amount"].sum())
    return {"incomes": incomes, "expenses": expenses, "net": incomes - expenses}
