import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.analytics.kpis import monthly_net_result, pf_pj_kpis, revenue_expense_by_month
from src.analytics.loader import load_transactions_df
from app.ui import page_header, plotly_layout, TYPE_COLORS, TIPO_LABEL
from app.export import generate_dashboard_pdf

st.set_page_config(page_title="Dashboard · Ponte Nexus", layout="wide", page_icon="💠")


@st.cache_data(ttl=30)
def _get_data():
    return load_transactions_df()


is_dark = page_header("Dashboard Geral", "Visão consolidada do período")
LAYOUT = plotly_layout(is_dark)

df = _get_data()

if df.empty:
    st.info("Nenhuma transação encontrada. Importe dados na página **Importação de Dados**.")
    st.stop()

# ── Indicadores principais ────────────────────────────────────────────────────
kpis = pf_pj_kpis(df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("💼 Total recebido pela PJ",  f"R$ {kpis['pj_income']:,.2f}")
c2.metric("👤 Total recebido pela PF",  f"R$ {kpis['pf_income']:,.2f}")
c3.metric("📉 Total de despesas",       f"R$ {kpis['expenses']:,.2f}")
c4.metric(
    "⚖️ Saldo do período",
    f"R$ {kpis['balance']:,.2f}",
    delta=f"R$ {kpis['balance']:,.2f}",
    delta_color="normal",
)

st.divider()

# ── Participação das empresas + Resultado mensal ───────────────────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown('<span class="nx-section-label">Participação das Empresas (PJ)</span>', unsafe_allow_html=True)
    pj_df = (
        df[df["transaction_type"] == "receita"]
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
            hole=0.45,
            color_discrete_sequence=["#64FFDA", "#4FC3F7", "#81C784", "#FFB74D", "#CE93D8"],
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont_size=12,
        )
        fig_pie.update_layout(**LAYOUT, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.markdown('<span class="nx-section-label">Resultado Mensal (Receitas − Despesas)</span>', unsafe_allow_html=True)
    monthly = monthly_net_result(df)
    if monthly.empty:
        st.info("Nenhum registro de receita ou despesa encontrado.")
    else:
        colors = ["#64FFDA" if v >= 0 else "#FF6B6B" for v in monthly["signed_amount"]]
        fig_bar = go.Figure(
            go.Bar(
                x=monthly["month"],
                y=monthly["signed_amount"],
                marker_color=colors,
                text=[f"R$ {v:,.0f}" for v in monthly["signed_amount"]],
                textposition="outside",
                textfont={"size": 11, "color": "#CCD6F6"},
            )
        )
        fig_bar.update_layout(
            **LAYOUT,
            yaxis_title="R$",
            xaxis_title="",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Evolução temporal: Receitas vs Despesas ───────────────────────────────────
st.markdown('<span class="nx-section-label">Evolução Temporal — Receitas e Despesas</span>', unsafe_allow_html=True)
rev_exp = revenue_expense_by_month(df)
if not rev_exp.empty:
    label_map = {"receita": "Receitas", "despesa": "Despesas"}
    rev_exp["tipo_label"] = rev_exp["transaction_type"].map(label_map)
    fig_area = px.area(
        rev_exp,
        x="month",
        y="amount",
        color="tipo_label",
        color_discrete_map={"Receitas": "#64FFDA", "Despesas": "#FF6B6B"},
        markers=True,
        labels={"amount": "R$", "month": "Mês", "tipo_label": "Tipo"},
    )
    fig_area.update_traces(line_width=2)
    fig_area.update_layout(
        **LAYOUT,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    st.plotly_chart(fig_area, use_container_width=True)

st.divider()

# ── Fluxo PF ↔ PJ: Pró-labore, Dividendos, Aportes ─────────────────────────
st.markdown('<span class="nx-section-label">Fluxo Financeiro PF ↔ PJ</span>', unsafe_allow_html=True)
_FLOW_TYPES = {"pro_labore", "dividendos", "aporte_pf_pj", "emprestimo_pf_pj"}
flow_df = (
    df[df["transaction_type"].isin(_FLOW_TYPES)]
    .groupby("transaction_type", as_index=False)["amount"]
    .sum()
)
if not flow_df.empty:
    flow_df["label"] = flow_df["transaction_type"].map(TIPO_LABEL).fillna(flow_df["transaction_type"])
    flow_df["cor"]   = flow_df["transaction_type"].map(TYPE_COLORS)
    fig_flow = px.bar(
        flow_df,
        x="label",
        y="amount",
        color="label",
        color_discrete_map=dict(zip(flow_df["label"], flow_df["cor"])),
        text=[f"R$ {v:,.0f}" for v in flow_df["amount"]],
        labels={"amount": "R$", "label": "Tipo"},
    )
    fig_flow.update_traces(textposition="outside", textfont_size=11)
    fig_flow.update_layout(**LAYOUT, showlegend=False, xaxis_title="")
    st.plotly_chart(fig_flow, use_container_width=True)

st.divider()

# ── Últimos 10 lançamentos ────────────────────────────────────────────────────
st.markdown('<span class="nx-section-label">Atividade Recente — Últimos 10 Lançamentos</span>', unsafe_allow_html=True)
_COL_MAP = {
    "date":               "Data",
    "descricao":          "Descrição",
    "category":           "Categoria",
    "source_entity_type": "Origem",
    "amount":             "Valor (R$)",
}
# fallback: loader usa 'description' como nome da coluna no df
if "description" in df.columns and "descricao" not in df.columns:
    df = df.rename(columns={"description": "descricao"})

cols_present = [c for c in _COL_MAP if c in df.columns]
last10 = df[cols_present].head(10).copy().rename(columns=_COL_MAP)
if "Data" in last10.columns:
    last10["Data"] = last10["Data"].dt.strftime("%d/%m/%Y")
if "Valor (R$)" in last10.columns:
    last10["Valor (R$)"] = last10["Valor (R$)"].map("R$ {:,.2f}".format)
st.dataframe(last10, use_container_width=True, hide_index=True)

st.divider()
pdf_bytes = generate_dashboard_pdf(kpis, monthly, last10)
st.download_button(
    label="📄 Exportar Dashboard PDF",
    data=pdf_bytes,
    file_name="ponte_nexus_dashboard.pdf",
    mime="application/pdf",
)
