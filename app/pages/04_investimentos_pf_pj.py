import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px

from src.analytics.loader import load_transactions_df

_TIPOS = {"investment_pf_to_pj", "loan_pf_to_pj"}


@st.cache_data(ttl=30)
def _get_data():
    df = load_transactions_df()
    return df[df["transaction_type"].isin(_TIPOS)].copy()


st.title("Investimentos PF na PJ")

df = _get_data()

if df.empty:
    st.info("Nenhum aporte ou emprestimo PF -> PJ encontrado.")
    st.stop()

total_aportes = float(df.loc[df["transaction_type"] == "investment_pf_to_pj", "amount"].sum())
total_emprestimos = float(df.loc[df["transaction_type"] == "loan_pf_to_pj", "amount"].sum())

col1, col2, col3 = st.columns(3)
col1.metric("Aportes", f"R$ {total_aportes:,.2f}")
col2.metric("Emprestimos", f"R$ {total_emprestimos:,.2f}")
col3.metric("Total Investido", f"R$ {total_aportes + total_emprestimos:,.2f}")

# Evolucao temporal
st.subheader("Evolucao Temporal")
df_plot = df.copy()
df_plot["month"] = df_plot["date"].dt.to_period("M").astype(str)
monthly = (
    df_plot.groupby(["month", "transaction_type"], as_index=False)["amount"]
    .sum()
    .sort_values("month")
)
fig = px.bar(
    monthly,
    x="month",
    y="amount",
    color="transaction_type",
    barmode="group",
    labels={"amount": "Total (R$)", "month": "Mes", "transaction_type": "Tipo"},
)
st.plotly_chart(fig, use_container_width=True)

# Tabela
st.subheader("Transacoes")
_COLS = ["date", "transaction_type", "source_entity_name", "destination_entity_name", "amount", "currency", "description"]
cols_present = [c for c in _COLS if c in df.columns]
st.dataframe(df[cols_present], use_container_width=True)
