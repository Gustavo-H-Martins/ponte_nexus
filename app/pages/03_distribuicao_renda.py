import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px

from src.analytics.loader import load_transactions_df

_TIPOS_RENDA = {"pro_labore", "dividend_distribution"}


@st.cache_data(ttl=30)
def _get_data():
    df = load_transactions_df()
    return df[df["transaction_type"].isin(_TIPOS_RENDA)].copy()


st.title("Distribuicao de Renda")

df = _get_data()

if df.empty:
    st.info("Nenhum registro de pro-labore ou dividendos encontrado.")
    st.stop()

total_pro_labore = float(df.loc[df["transaction_type"] == "pro_labore", "amount"].sum())
total_dividendos = float(df.loc[df["transaction_type"] == "dividend_distribution", "amount"].sum())

col1, col2, col3 = st.columns(3)
col1.metric("Pro-Labore", f"R$ {total_pro_labore:,.2f}")
col2.metric("Dividendos", f"R$ {total_dividendos:,.2f}")
col3.metric("Total Distribuido", f"R$ {total_pro_labore + total_dividendos:,.2f}")

# Evolucao mensal
st.subheader("Evolucao Mensal")
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

# Proporcao
st.subheader("Proporcao")
by_type = df.groupby("transaction_type", as_index=False)["amount"].sum()
fig2 = px.pie(by_type, names="transaction_type", values="amount")
st.plotly_chart(fig2, use_container_width=True)

# Tabela
st.subheader("Registros")
_COLS = ["date", "transaction_type", "source_entity_name", "destination_entity_name", "amount", "currency"]
cols_present = [c for c in _COLS if c in df.columns]
st.dataframe(df[cols_present], use_container_width=True)
