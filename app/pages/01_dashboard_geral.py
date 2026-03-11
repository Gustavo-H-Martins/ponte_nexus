import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px

from src.analytics.kpis import monthly_net_result, pf_pj_kpis
from src.analytics.loader import load_transactions_df


@st.cache_data(ttl=30)
def _get_data():
    return load_transactions_df()


st.title("Dashboard Geral")
st.caption("Visão consolidada do período")

df = _get_data()

if df.empty:
    st.info("Nenhuma transação encontrada. Importe dados na página Importação de Dados.")
    st.stop()

# --- Indicadores principais do período ---
kpis = pf_pj_kpis(df)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total recebido pela PJ", f"R$ {kpis['pj_income']:,.2f}")
col2.metric("Total recebido pela PF", f"R$ {kpis['pf_income']:,.2f}")
col3.metric("Total de despesas", f"R$ {kpis['expenses']:,.2f}")
col4.metric(
    "Saldo do período",
    f"R$ {kpis['balance']:,.2f}",
    delta=f"R$ {kpis['balance']:,.2f}",
    delta_color="normal",
)

st.divider()

# --- Participação das empresas e resultado mensal lado a lado ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Participação das Empresas (PJ)")
    pj_df = (
        df[df["transaction_type"] == "income"]
        .groupby("source_entity_name", as_index=False)["amount"]
        .sum()
    )
    if pj_df.empty:
        st.info("Nenhuma receita de PJ encontrada.")
    else:
        fig_pie = px.pie(
            pj_df,
            names="source_entity_name",
            values="amount",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, margin={"t": 10, "b": 10})
        st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("Resultado Mensal")
    monthly = monthly_net_result(df)
    if monthly.empty:
        st.info("Nenhum registro de receita ou despesa encontrado.")
    else:
        fig_bar = px.bar(
            monthly,
            x="month",
            y="signed_amount",
            labels={"signed_amount": "Resultado (R$)", "month": "Mês"},
            color_discrete_sequence=["#2196F3"],
        )
        fig_bar.update_layout(margin={"t": 10, "b": 10})
        st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# --- Últimos 10 lançamentos ---
st.subheader("Últimos Lançamentos")
_COL_MAP = {
    "date": "Data",
    "description": "Descrição",
    "category": "Categoria",
    "amount": "Valor (R$)",
    "source_entity_type": "Origem",
}
cols_present = [c for c in _COL_MAP if c in df.columns]
last10 = df[cols_present].head(10).copy().rename(columns=_COL_MAP)
if "Data" in last10.columns:
    last10["Data"] = last10["Data"].dt.strftime("%d/%m/%Y")
if "Valor (R$)" in last10.columns:
    last10["Valor (R$)"] = last10["Valor (R$)"].map("R$ {:,.2f}".format)
st.dataframe(last10, use_container_width=True, hide_index=True)
