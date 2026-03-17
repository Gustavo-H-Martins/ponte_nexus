from decimal import Decimal

import streamlit as st

from app.ui import page_header, is_reader
from src.analytics.loader import load_transactions_df
from src.services.budget_service import BudgetService
from src.services.catalog_service import CatalogService

st.set_page_config(page_title="Orçamento · Ponte Nexus", layout="wide", page_icon="🎯")

page_header("Orçamento", "Defina limites de gastos por categoria e acompanhe seu progresso")

_budget_svc = BudgetService(owner_id=st.session_state.get("effective_owner_id"))
_catalog    = CatalogService(owner_id=st.session_state.get("effective_owner_id"))


@st.cache_data(ttl=30)
def _get_categories(owner_id: int | None) -> list[dict]:
    return [{"id": c.id, "name": c.name} for c in CatalogService(owner_id=owner_id).list_categories()]


@st.cache_data(ttl=30)
def _get_data(owner_id: int | None):
    return load_transactions_df(owner_id=owner_id)


categories = _get_categories(st.session_state.get("effective_owner_id"))

if not categories:
    st.info(
        "📭 Nenhuma categoria cadastrada ainda. "
        "Crie categorias em **Registrar Transação → ⚙️ Configurações** antes de definir orçamentos."
    )
    if st.button("✏️ Ir para Configurações", type="primary"):
        st.switch_page("pages/07_novo_lancamento.py")
    st.stop()

# ── Seletor de mês de referência ──────────────────────────────────────────────
df = _get_data(st.session_state.get("effective_owner_id"))
import datetime
current_month = datetime.date.today().strftime("%Y-%m")

if not df.empty:
    available_months = sorted(
        df["date"].dt.to_period("M").astype(str).unique().tolist(), reverse=True
    )
    # Inclui mês atual mesmo que não haja dados ainda
    if current_month not in available_months:
        available_months.insert(0, current_month)
else:
    available_months = [current_month]

selected_month = st.selectbox(
    "Mês de referência",
    options=available_months,
    index=0,
    help="Selecione o mês para definir e acompanhar orçamentos",
)

st.divider()

# ── Seção 1: Definir / atualizar meta ────────────────────────────────────────
if not is_reader():
    st.markdown('<span class="nx-section-label">Definir meta de gasto</span>', unsafe_allow_html=True)

    with st.form("form_budget"):
        col_b1, col_b2, col_b3 = st.columns([3, 2, 1])
        with col_b1:
            cat_names   = [c["name"] for c in categories]
            cat_label   = st.selectbox("Categoria", cat_names)
            cat_sel     = next((c for c in categories if c["name"] == cat_label), None)
        with col_b2:
            limit_value = st.number_input(
                "Limite mensal (R$)",
                min_value=1.0,
                step=50.0,
                format="%.2f",
                help="Valor máximo de gastos nessa categoria no mês selecionado",
            )
        with col_b3:
            st.markdown("")
            st.markdown("")
            salvar = st.form_submit_button("💾 Salvar", type="primary")

        if salvar and cat_sel:
            try:
                _budget_svc.set_budget(
                    category_id=cat_sel["id"],
                    year_month=selected_month,
                    limit_amount=Decimal(str(limit_value)),
                )
                st.toast(f"Meta de R$ {limit_value:,.2f} salva para '{cat_label}'!", icon="🎯")
                st.cache_data.clear()
                st.rerun()
            except Exception as exc:
                st.error(f"Erro ao salvar orçamento: {exc}")

st.divider()

# ── Seção 2: Acompanhamento do mês selecionado ────────────────────────────────
st.markdown('<span class="nx-section-label">Acompanhamento do mês</span>', unsafe_allow_html=True)

utilization = _budget_svc.get_utilization(df, selected_month)

if not utilization:
    st.info(
        f"📭 Nenhum orçamento definido para {selected_month}. "
        "Use o formulário acima para criar sua primeira meta de gasto."
    )
    st.stop()

# Renderiza uma linha por categoria com barra de progresso
for item in utilization:
    cat_name = item["category"]
    spent    = item["spent"]
    limit    = item["limit"]
    pct      = item["pct"]
    status   = item["status"]

    col_name, col_bar, col_values = st.columns([3, 5, 2])

    with col_name:
        icon = "🔴" if status == "danger" else "🟠" if status == "warning" else "🟢"
        st.markdown(f"**{icon} {cat_name}**")

    with col_bar:
        # Normaliza para [0, 1] mas trava em 1.0 para não estourar a barra
        bar_pct = min(pct / 100, 1.0)
        st.progress(bar_pct)

    with col_values:
        st.markdown(f"R$ {spent:,.2f} / R$ {limit:,.2f}")
        if status == "danger":
            st.caption(f"🔴 {pct:.0f}% — Limite ultrapassado")
        elif status == "warning":
            st.caption(f"🟠 {pct:.0f}% — Atenção")
        else:
            st.caption(f"🟢 {pct:.0f}% utilizado")

st.divider()

# ── Resumo consolidado ───────────────────────────────────────────────────────
total_limit = sum(i["limit"]  for i in utilization)
total_spent = sum(i["spent"]  for i in utilization)
over_budget = [i for i in utilization if i["status"] == "danger"]

c1, c2, c3 = st.columns(3)
c1.metric("💰 Total orçado", f"R$ {total_limit:,.2f}")
c2.metric("📉 Total gasto",  f"R$ {total_spent:,.2f}")
c3.metric(
    "⚖️ Saldo disponível",
    f"R$ {total_limit - total_spent:,.2f}",
    delta=f"{(total_spent / total_limit * 100):.0f}% utilizado" if total_limit > 0 else None,
    delta_color="inverse",
)

if over_budget:
    cats_over = ", ".join(i["category"] for i in over_budget)
    st.warning(
        f"⚠️ {len(over_budget)} categoria(s) ultrapassaram o limite: **{cats_over}**. "
        "Revise seus gastos ou ajuste as metas."
    )

with st.expander("ℹ️ Como interpretar as cores?", expanded=False):
    st.markdown("""
    🟢 **Verde** — gastos dentro do limite (abaixo de 70%)

    🟠 **Laranja** — atenção: você já usou entre 70% e 90% do orçamento

    🔴 **Vermelho** — limite ultrapassado (acima de 90%)

    **Dica:** Defina metas um pouco abaixo do seu gasto real para criar uma margem de segurança.
    """)
