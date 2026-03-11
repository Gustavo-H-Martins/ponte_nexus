import pandas as pd


def monthly_net_result(df: pd.DataFrame) -> pd.DataFrame:
    """Resultado liquido mensal considerando apenas income e expense."""
    data = df[df["transaction_type"].isin({"income", "expense"})].copy()
    if data.empty:
        return pd.DataFrame(columns=["month", "signed_amount"])

    data["month"] = pd.to_datetime(data["date"]).dt.to_period("M").astype(str)
    data["signed_amount"] = data.apply(
        lambda row: row["amount"] if row["transaction_type"] == "income" else -row["amount"],
        axis=1,
    )
    return data.groupby("month", as_index=False)["signed_amount"].sum().sort_values("month")


def income_expense_summary(df: pd.DataFrame) -> dict[str, float]:
    """Retorna totais de receita, despesa e resultado liquido."""
    if df.empty:
        return {"income": 0.0, "expense": 0.0, "net": 0.0}
    income = float(df.loc[df["transaction_type"] == "income", "amount"].sum())
    expense = float(df.loc[df["transaction_type"] == "expense", "amount"].sum())
    return {"income": income, "expense": expense, "net": income - expense}


def pf_pj_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Retorna KPIs consolidados PF/PJ do periodo.

    - pj_income: total de receitas operacionais da PJ (tipo 'income')
    - pf_income: total recebido pela PF via pro-labore e dividendos
    - expenses: total de despesas da PJ
    - balance: resultado liquido do periodo (pj_income - expenses)
    """
    if df.empty:
        return {"pj_income": 0.0, "pf_income": 0.0, "expenses": 0.0, "balance": 0.0}

    pj_income = float(
        df.loc[df["transaction_type"] == "income", "amount"].sum()
    )
    pf_income = float(
        df.loc[
            df["transaction_type"].isin({"pro_labore", "dividend_distribution"}),
            "amount",
        ].sum()
    )
    expenses = float(df.loc[df["transaction_type"] == "expense", "amount"].sum())
    return {
        "pj_income": pj_income,
        "pf_income": pf_income,
        "expenses": expenses,
        "balance": pj_income - expenses,
    }
