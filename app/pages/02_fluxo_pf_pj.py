import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px

from src.analytics.cashflow import pf_pj_flow
from src.analytics.loader import load_transactions_df
from src.analytics.pf_pj_analysis import summarize_pf_pj_direction
from app.ui import page_header, plotly_layout, TIPO_LABEL, TYPE_COLORS

st.set_page_config(page_title="Fluxo PF ↔ PJ · Ponte Nexus", layout="wide", page_icon="💠")


@st.cache_data(ttl=30)
def _get_flow():
    return pf_pj_flow(load_transactions_df())


is_dark = page_header("Fluxo PF ↔ PJ", "Transferências, aportes e retiradas entre Pessoa Física e Jurídica")
LAYOUT = plotly_layout(is_dark)

df_flow = _get_flow()

if df_flow.empty:
    st.info(
        "Nenhum fluxo PF ↔ PJ encontrado. "
        "Importe transações de transferência, aporte ou distribuição."
    )
    st.stop()

# Totais por direção
summary = summarize_pf_pj_direction(df_flow)
pf_to_pj = float(summary.loc[summary["direction"] == "pf_to_pj", "amount"].values[0])
pj_to_pf = float(summary.loc[summary["direction"] == "pj_to_pf", "amount"].values[0])

col1, col2, col3 = st.columns(3)
col1.metric("👤→🏢 PF → PJ (aportes / empréstimos)", f"R$ {pf_to_pj:,.2f}")
col2.metric("🏢→👤 PJ → PF (retiradas / dividendos)", f"R$ {pj_to_pf:,.2f}")
col3.metric("Saldo retornado à PF", f"R$ {pj_to_pf - pf_to_pj:,.2f}")

st.divider()

# Volume por tipo de fluxo
st.markdown('<span class="nx-section-label">Volume por Tipo de Fluxo</span>', unsafe_allow_html=True)
by_type = (
    df_flow.groupby("transaction_type", as_index=False)["amount"]
    .sum()
    .sort_values("amount", ascending=False)
)
by_type["label"] = by_type["transaction_type"].map(TIPO_LABEL).fillna(by_type["transaction_type"])
by_type["cor"]   = by_type["transaction_type"].map(TYPE_COLORS)
fig = px.bar(
    by_type,
    x="label",
    y="amount",
    color="label",
    color_discrete_map=dict(zip(by_type["label"], by_type["cor"])),
    text=[f"R$ {v:,.0f}" for v in by_type["amount"]],
    labels={"amount": "R$", "label": "Tipo"},
)
fig.update_traces(textposition="outside")
fig.update_layout(**LAYOUT, showlegend=False, xaxis_title="")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Evolução mensal por tipo
st.markdown('<span class="nx-section-label">Evolução Mensal por Tipo</span>', unsafe_allow_html=True)
df_plot = df_flow.copy()
df_plot["month"] = df_plot["date"].dt.to_period("M").astype(str)
monthly = (
    df_plot.groupby(["month", "transaction_type"], as_index=False)["amount"]
    .sum()
    .sort_values("month")
)
monthly["label"] = monthly["transaction_type"].map(TIPO_LABEL).fillna(monthly["transaction_type"])
fig2 = px.bar(
    monthly,
    x="month",
    y="amount",
    color="label",
    barmode="group",
    color_discrete_sequence=["#64FFDA", "#4FC3F7", "#81C784", "#FFB74D", "#CE93D8", "#FFF176"],
    labels={"amount": "R$", "month": "Mês", "label": "Tipo"},
)
fig2.update_layout(**LAYOUT)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Tabela
st.markdown('<span class="nx-section-label">Transações de Fluxo</span>', unsafe_allow_html=True)
_COLS = ["date", "transaction_type", "source_entity_name", "destination_entity_name", "amount", "currency"]
cols_present = [c for c in _COLS if c in df_flow.columns]
st.dataframe(df_flow[cols_present], use_container_width=True, hide_index=True)
