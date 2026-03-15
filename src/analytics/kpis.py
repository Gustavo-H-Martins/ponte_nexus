import pandas as pd


def monthly_net_result(df: pd.DataFrame) -> pd.DataFrame:
    """Resultado líquido mensal considerando apenas receita e despesa."""
    data = df[df["transaction_type"].isin({"receita", "despesa"})].copy()
    if data.empty:
        return pd.DataFrame(columns=["month", "signed_amount"])

    data["month"] = pd.to_datetime(data["date"]).dt.to_period("M").astype(str)
    data["signed_amount"] = data.apply(
        lambda row: row["amount"] if row["transaction_type"] == "receita" else -row["amount"],
        axis=1,
    )
    return data.groupby("month", as_index=False)["signed_amount"].sum().sort_values("month")


def income_expense_summary(df: pd.DataFrame) -> dict[str, float]:
    """Retorna totais de receita, despesa e resultado líquido."""
    if df.empty:
        return {"income": 0.0, "expense": 0.0, "net": 0.0}
    income = float(df.loc[df["transaction_type"] == "receita", "amount"].sum())
    expense = float(df.loc[df["transaction_type"] == "despesa", "amount"].sum())
    return {"income": income, "expense": expense, "net": income - expense}


def pf_pj_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Retorna KPIs consolidados PF/PJ do período.

    - pj_income: total de receitas operacionais da PJ (tipo 'receita')
    - pf_income: total recebido pela PF via pró-labore e dividendos
    - expenses: total de despesas da PJ
    - balance: resultado líquido do período (pj_income - expenses)
    """
    if df.empty:
        return {"pj_income": 0.0, "pf_income": 0.0, "expenses": 0.0, "balance": 0.0}

    pj_income = float(
        df.loc[df["transaction_type"] == "receita", "amount"].sum()
    )
    pf_income = float(
        df.loc[
            df["transaction_type"].isin({"pro_labore", "dividendos"}),
            "amount",
        ].sum()
    )
    expenses = float(df.loc[df["transaction_type"] == "despesa", "amount"].sum())
    return {
        "pj_income": pj_income,
        "pf_income": pf_income,
        "expenses": expenses,
        "balance": pj_income - expenses,
    }


def revenue_expense_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna receitas e despesas mensais para gráfico de evolução temporal."""
    data = df[df["transaction_type"].isin({"receita", "despesa"})].copy()
    if data.empty:
        return pd.DataFrame(columns=["month", "transaction_type", "amount"])
    data["month"] = pd.to_datetime(data["date"]).dt.to_period("M").astype(str)
    return (
        data.groupby(["month", "transaction_type"], as_index=False)["amount"]
        .sum()
        .sort_values("month")
    )


def income_by_source(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna total de receitas por categoria (fonte), ordenado decrescente.

    Considera tipos de receita: 'receita', 'pro_labore', 'dividendos'.
    Requer coluna 'category' no DataFrame.
    """
    income_types = {"receita", "pro_labore", "dividendos"}
    data = df[df["transaction_type"].isin(income_types)].copy()
    if data.empty:
        return pd.DataFrame(columns=["category", "amount"])
    return (
        data.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )


def top_expense_categories(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Retorna as N categorias com maior volume de despesa, ordenadas decrescente.

    Requer coluna 'category' no DataFrame.
    """
    data = df[df["transaction_type"] == "despesa"].copy()
    if data.empty:
        return pd.DataFrame(columns=["category", "amount"])
    return (
        data.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
        .head(n)
    )


def period_comparison(
    df: pd.DataFrame, current_period: str, previous_period: str
) -> dict[str, float]:
    """Compara receita, despesa e saldo entre dois períodos no formato YYYY-MM.

    Retorna deltas absolutos e percentuais para cada indicador.
    """
    def _kpis_for_period(period: str) -> dict[str, float]:
        mask = pd.to_datetime(df["date"]).dt.to_period("M").astype(str) == period
        return income_expense_summary(df[mask])

    current = _kpis_for_period(current_period)
    previous = _kpis_for_period(previous_period)

    def _pct_change(curr: float, prev: float) -> float:
        if prev == 0.0:
            return 0.0
        return round((curr - prev) / abs(prev) * 100, 2)

    return {
        "income_current": current["income"],
        "income_previous": previous["income"],
        "income_delta_pct": _pct_change(current["income"], previous["income"]),
        "expense_current": current["expense"],
        "expense_previous": previous["expense"],
        "expense_delta_pct": _pct_change(current["expense"], previous["expense"]),
        "net_current": current["net"],
        "net_previous": previous["net"],
        "net_delta_pct": _pct_change(current["net"], previous["net"]),
    }
