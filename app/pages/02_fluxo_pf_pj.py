import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px

from src.analytics.cashflow import pf_pj_flow
from src.analytics.loader import load_transactions_df
from src.analytics.pf_pj_analysis import summarize_pf_pj_direction


@st.cache_data(ttl=30)
def _get_flow():
    return pf_pj_flow(load_transactions_df())


st.title("Fluxo PF <-> PJ")

df_flow = _get_flow()

if df_flow.empty:
    st.info(
        "Nenhum fluxo PF <-> PJ encontrado. "
        "Importe transacoes de transferencia, aporte ou distribuicao."
    )
    st.stop()

# Totais por direcao
summary = summarize_pf_pj_direction(df_flow)
pf_to_pj = float(summary.loc[summary["direction"] == "pf_to_pj", "amount"].values[0])
pj_to_pf = float(summary.loc[summary["direction"] == "pj_to_pf", "amount"].values[0])

col1, col2, col3 = st.columns(3)
col1.metric("PF -> PJ (aportes / emprestimos)", f"R$ {pf_to_pj:,.2f}")
col2.metric("PJ -> PF (retiradas / dividendos)", f"R$ {pj_to_pf:,.2f}")
col3.metric("Saldo retornado a PF", f"R$ {pj_to_pf - pf_to_pj:,.2f}")

# Por tipo de fluxo
st.subheader("Volume por Tipo de Fluxo")
by_type = (
    df_flow.groupby("transaction_type", as_index=False)["amount"]
    .sum()
    .sort_values("amount", ascending=False)
)
fig = px.bar(
    by_type,
    x="transaction_type",
    y="amount",
    labels={"amount": "Total (R$)", "transaction_type": "Tipo"},
)
st.plotly_chart(fig, use_container_width=True)

# Evolucao mensal
st.subheader("Evolucao Mensal por Tipo")
df_plot = df_flow.copy()
df_plot["month"] = df_plot["date"].dt.to_period("M").astype(str)
monthly = (
    df_plot.groupby(["month", "transaction_type"], as_index=False)["amount"]
    .sum()
    .sort_values("month")
)
fig2 = px.bar(
    monthly,
    x="month",
    y="amount",
    color="transaction_type",
    barmode="group",
    labels={"amount": "Total (R$)", "month": "Mes", "transaction_type": "Tipo"},
)
st.plotly_chart(fig2, use_container_width=True)

# Tabela
st.subheader("Transacoes de Fluxo")
_COLS = ["date", "transaction_type", "source_entity_name", "destination_entity_name", "amount", "currency"]
cols_present = [c for c in _COLS if c in df_flow.columns]
st.dataframe(df_flow[cols_present], use_container_width=True)
