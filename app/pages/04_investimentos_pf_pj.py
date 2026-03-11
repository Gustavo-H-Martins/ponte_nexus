import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px

from src.analytics.loader import load_transactions_df
from app.ui import page_header, plotly_layout, TYPE_COLORS, TIPO_LABEL

_TIPOS = {"aporte_pf_pj", "emprestimo_pf_pj"}

st.set_page_config(page_title="Investimentos PF na PJ · Ponte Nexus", layout="wide", page_icon="💠")


@st.cache_data(ttl=30)
def _get_data():
    df = load_transactions_df()
    return df[df["transaction_type"].isin(_TIPOS)].copy()


is_dark = page_header("Investimentos PF na PJ", "Aportes e empréstimos da Pessoa Física para a Pessoa Jurídica")
LAYOUT = plotly_layout(is_dark)

df = _get_data()

if df.empty:
    st.info("Nenhum aporte ou empréstimo PF → PJ encontrado.")
    st.stop()

total_aportes    = float(df.loc[df["transaction_type"] == "aporte_pf_pj",    "amount"].sum())
total_emprestimos = float(df.loc[df["transaction_type"] == "emprestimo_pf_pj", "amount"].sum())

col1, col2, col3 = st.columns(3)
col1.metric("📊 Aportes",          f"R$ {total_aportes:,.2f}")
col2.metric("🏦 Empréstimos",       f"R$ {total_emprestimos:,.2f}")
col3.metric("∑ Total Investido", f"R$ {total_aportes + total_emprestimos:,.2f}")

st.divider()

# Evolução temporal
st.markdown('<span class="nx-section-label">Evolução Temporal</span>', unsafe_allow_html=True)
df_plot = df.copy()
df_plot["month"] = df_plot["date"].dt.to_period("M").astype(str)
monthly = (
    df_plot.groupby(["month", "transaction_type"], as_index=False)["amount"]
    .sum()
    .sort_values("month")
)
monthly["label"] = monthly["transaction_type"].map(TIPO_LABEL).fillna(monthly["transaction_type"])
fig = px.bar(
    monthly,
    x="month",
    y="amount",
    color="label",
    barmode="group",
    color_discrete_map={"Aporte PF→PJ": TYPE_COLORS["aporte_pf_pj"], "Empréstimo PF→PJ": TYPE_COLORS["emprestimo_pf_pj"]},
    labels={"amount": "R$", "month": "Mês", "label": "Tipo"},
)
fig.update_layout(**LAYOUT)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Tabela
st.markdown('<span class="nx-section-label">Transações</span>', unsafe_allow_html=True)
_COLS = ["date", "transaction_type", "source_entity_name", "destination_entity_name", "amount", "currency", "description"]
cols_present = [c for c in _COLS if c in df.columns]
st.dataframe(df[cols_present], use_container_width=True, hide_index=True)
