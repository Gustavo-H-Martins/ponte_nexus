import pandas as pd
from sqlalchemy import text

from src.fin_dashboard.core.database import engine


def load_transactions() -> pd.DataFrame:
    query = text(
        """
        SELECT
            id, nome_entidade, data, descricao, categoria, tipo_transacao, valor, conta_origem
        FROM transactions
        ORDER BY data DESC, id DESC
        """
    )
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def kpis(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {"incomes": 0.0, "expenses": 0.0, "net": 0.0}
    incomes = float(df.loc[df["tipo_transacao"] == "receita", "valor"].sum())
    expenses = float(df.loc[df["tipo_transacao"] == "despesa", "valor"].sum())
    return {"incomes": incomes, "expenses": expenses, "net": incomes - expenses}
