import streamlit as st
import plotly.express as px

from src.analytics.loader import load_transactions_df
from app.ui import FAVICON_IMG,  page_header, plotly_layout, TYPE_COLORS, TIPO_LABEL

_TIPOS = {"aporte_pf_pj", "emprestimo_pf_pj"}

st.set_page_config(page_title="Aportes na Empresa · Inside Cash", layout="wide", page_icon=FAVICON_IMG or "📈")


@st.cache_data(ttl=30)
def _get_data(owner_id: int | None):
    df = load_transactions_df(owner_id=owner_id)
    return df[df["transaction_type"].isin(_TIPOS)].copy()


is_dark = page_header("Aportes na Empresa", "Capital que você investiu na empresa")
LAYOUT = plotly_layout(is_dark)

df = _get_data(st.session_state.get("effective_owner_id"))

if df.empty:
    st.info(
        "Nenhum aporte ou empréstimo da sua parte para a empresa ainda. "
        "Registre um aporte de capital ou empréstimo para visualizar esta página."
    )
    col_a, col_b, _ = st.columns([2, 2, 4])
    with col_a:
        if st.button("Registrar aporte", type="primary"):
            st.switch_page("pages/07_novo_lancamento.py")
    with col_b:
        if st.button("Importar extrato"):
            st.switch_page("pages/05_importacao_dados.py")
    st.stop()

total_aportes    = float(df.loc[df["transaction_type"] == "aporte_pf_pj",    "amount"].sum())
total_emprestimos = float(df.loc[df["transaction_type"] == "emprestimo_pf_pj", "amount"].sum())

col1, col2, col3 = st.columns(3)
col1.metric("📈 Aportes",         f"R$ {total_aportes:,.2f}")
col2.metric("💳 Empréstimos",      f"R$ {total_emprestimos:,.2f}")
col3.metric("∑ Total Investido",  f"R$ {total_aportes + total_emprestimos:,.2f}")

with st.expander("ℹ️ Aporte vs Empréstimo — qual a diferença?", expanded=False):
    st.markdown("""
    **Aporte de capital** — você coloca dinheiro na empresa como investimento permanente.  
    Esse valor aumenta o patrimônio líquido da empresa e não precisa ser devolvido.

    **Empréstimo PF → PJ** — você empresta dinheiro para a empresa com a intenção de receber de volta.  
    A empresa registra como dívida (passivo) e você como crédito a receber.

    **Dica:** Formalize empréstimos em contrato assinado para evitar questionamentos fiscais.
    """)

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
