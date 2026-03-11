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
