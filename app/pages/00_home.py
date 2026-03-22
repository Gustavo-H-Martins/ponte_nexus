import sys
from pathlib import Path
_REPO_ROOT = Path(__file__).parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd
import streamlit as st

from app.ui import FAVICON_IMG, page_header
from src.analytics.kpis import pf_pj_kpis, income_expense_summary
from src.analytics.loader import load_transactions_df

st.set_page_config(page_title="Início · Inside Money", layout="wide", page_icon=FAVICON_IMG)


@st.cache_data(ttl=30)
def _get_kpis(owner_id: int | None) -> tuple[dict, dict]:
    """Retorna KPIs do mês corrente e do total."""
    df = load_transactions_df(owner_id=owner_id)
    if df.empty:
        empty = {"income": 0.0, "expense": 0.0, "net": 0.0}
        return empty, {"pj_income": 0.0, "pf_income": 0.0, "expenses": 0.0, "balance": 0.0}

    now = pd.Timestamp.now()
    df_month = df[(df["date"].dt.year == now.year) & (df["date"].dt.month == now.month)]
    return income_expense_summary(df_month), pf_pj_kpis(df_month)


def _fmt_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


is_dark = page_header("Início", "Visão consolidada do seu período atual")

owner_id = st.session_state.get("effective_owner_id")
username = st.session_state.get("username", "")

summary, kpis = _get_kpis(owner_id)

# ── Saudação personalizada ─────────────────────────────────────────────────────
st.markdown(f"### Olá, **{username}**")
st.caption(f"Resumo de {pd.Timestamp.now().strftime('%B de %Y').capitalize()}")

st.divider()

# ── KPIs do mês ───────────────────────────────────────────────────────────────
st.markdown('<span class="nx-section-label">Mês atual</span>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Receita Total", _fmt_brl(kpis["pj_income"] + summary["income"]))
with col2:
    st.metric("Despesas", _fmt_brl(summary["expense"]))
with col3:
    net = summary["income"] - summary["expense"]
    st.metric("Resultado Líquido", _fmt_brl(net), delta=f"R$ {net:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if net != 0 else None)
with col4:
    st.metric("Remuneração PF", _fmt_brl(kpis["pf_income"]))

st.divider()

# ── Acesso rápido ─────────────────────────────────────────────────────────────
st.markdown('<span class="nx-section-label">Acesso rápido</span>', unsafe_allow_html=True)

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    if st.button("Registrar Transação", use_container_width=True, type="primary"):
        st.switch_page("pages/07_novo_lancamento.py")

with col_b:
    if st.button("Importar Extrato", use_container_width=True):
        st.switch_page("pages/05_importacao_dados.py")

with col_c:
    if st.button("Ver Extrato", use_container_width=True):
        st.switch_page("pages/06_lancamentos.py")

with col_d:
    if st.button("Visão Geral", use_container_width=True):
        st.switch_page("pages/01_dashboard_geral.py")
