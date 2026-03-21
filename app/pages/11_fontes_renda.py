from decimal import Decimal

import pandas as pd
import plotly.express as px
import streamlit as st

from app.ui import FAVICON_IMG,  page_header, plotly_layout, is_reader
from src.analytics.loader import load_transactions_df
from src.domain.enums import IncomeSourceType
from src.services.catalog_service import CatalogService

st.set_page_config(page_title="Fontes de Renda · Inside Money", layout="wide", page_icon=FAVICON_IMG or "💵")

is_dark = page_header("Fontes de Renda", "De onde vem seu dinheiro — e quanto cada fonte contribui")
LAYOUT = plotly_layout(is_dark)

_catalog = CatalogService(owner_id=st.session_state.get("effective_owner_id"))

_SOURCE_LABELS: dict[str, str] = {
    IncomeSourceType.SALARIO.value:      "Salário (CLT)",
    IncomeSourceType.FREELANCE.value:    "Freelance / Autônomo",
    IncomeSourceType.DIVIDENDOS.value:   "Dividendos da empresa",
    IncomeSourceType.PRO_LABORE.value:   "Pró-labore",
    IncomeSourceType.INVESTIMENTO.value: "Investimentos",
    IncomeSourceType.ALUGUEL.value:      "Aluguel",
    IncomeSourceType.OUTRO.value:        "Outra fonte",
}

_INCOME_TX_TYPES = {"receita", "pro_labore", "dividendos"}


@st.cache_data(ttl=30)
def _get_entities(owner_id: int | None) -> list[dict]:
    all_entities = CatalogService(owner_id=owner_id).list_entities()
    return [{"id": e.id, "name": e.name, "type": e.entity_type} for e in all_entities]


@st.cache_data(ttl=30)
def _get_sources(owner_id: int | None) -> list[dict]:
    sources = CatalogService(owner_id=owner_id).list_income_sources()
    return [
        {
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "entity_id": s.entity_id,
            "is_active": s.is_active,
        }
        for s in sources
    ]


@st.cache_data(ttl=30)
def _get_data(owner_id: int | None) -> pd.DataFrame:
    return load_transactions_df(owner_id=owner_id)


def _reload() -> None:
    _get_entities.clear()
    _get_sources.clear()
    _get_data.clear()


entities = _get_entities(st.session_state.get("effective_owner_id"))
sources  = _get_sources(st.session_state.get("effective_owner_id"))
df_all   = _get_data(st.session_state.get("effective_owner_id"))

# ── Tabs: Gestão e Análise ─────────────────────────────────────────────────────
tab_analysis, tab_manage = st.tabs(["📊 Análise por Fonte", "⚙️ Gerenciar Fontes"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANÁLISE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_analysis:
    if df_all.empty:
        st.info(
            "📭 Nenhuma transação encontrada. Importe ou registre dados para visualizar a análise."
        )
        if st.button("📂 Importar extrato", type="primary"):
            st.switch_page("pages/05_importacao_dados.py")
    else:
        # Filtra apenas transações de receita / remuneração
        df_income = df_all[df_all["transaction_type"].isin(_INCOME_TX_TYPES)].copy()

        if df_income.empty:
            st.info(
                "📭 Nenhuma receita encontrada no período. "
                "Registre receitas, pró-labore ou dividendos para ver a análise."
            )
        else:
            # Filtro de período
            available_months = sorted(
                df_income["date"].dt.to_period("M").astype(str).unique().tolist()
            )
            col_f1, col_f2, _ = st.columns([2, 2, 4])
            with col_f1:
                period_start = st.selectbox(
                    "De", available_months, index=0
                )
            with col_f2:
                period_end = st.selectbox(
                    "Até", available_months, index=len(available_months) - 1
                )

            mask = (
                (df_income["date"].dt.to_period("M").astype(str) >= period_start)
                & (df_income["date"].dt.to_period("M").astype(str) <= period_end)
            )
            df_period = df_income[mask].copy()

            if df_period.empty:
                st.info("Nenhuma receita no período selecionado.")
            else:
                total_income = float(df_period["amount"].sum())

                # ── KPIs ─────────────────────────────────────────────────────
                col_k1, col_k2, col_k3 = st.columns(3)
                col_k1.metric("💰 Total de receitas", f"R$ {total_income:,.2f}")
                col_k2.metric("📅 Meses analisados", str(len(available_months)))
                media_mensal = total_income / max(len(available_months), 1)
                col_k3.metric("📊 Média mensal", f"R$ {media_mensal:,.2f}")

                st.divider()

                # ── Receita por tipo de transação ─────────────────────────────
                st.markdown('<span class="nx-section-label">Receita por tipo</span>', unsafe_allow_html=True)
                by_type = (
                    df_period.groupby("transaction_type", as_index=False)["amount"]
                    .sum()
                    .sort_values("amount", ascending=False)
                )
                _TX_LABELS = {
                    "receita":   "Receitas gerais",
                    "pro_labore": "Pró-labore",
                    "dividendos": "Dividendos",
                }
                by_type["label"] = by_type["transaction_type"].map(_TX_LABELS).fillna(by_type["transaction_type"])
                by_type["pct"] = (by_type["amount"] / total_income * 100).round(1)

                col_pie, col_bar = st.columns(2, gap="large")
                with col_pie:
                    fig_pie = px.pie(
                        by_type,
                        names="label",
                        values="amount",
                        hole=0.45,
                        color_discrete_sequence=["#64FFDA", "#4FC3F7", "#81C784", "#FFB74D"],
                    )
                    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                    fig_pie.update_layout(**LAYOUT, showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col_bar:
                    # Evolução mensal de receitas
                    df_monthly = df_period.copy()
                    df_monthly["month"] = df_monthly["date"].dt.to_period("M").astype(str)
                    monthly_agg = (
                        df_monthly.groupby(["month", "transaction_type"], as_index=False)["amount"]
                        .sum()
                        .sort_values("month")
                    )
                    monthly_agg["label"] = monthly_agg["transaction_type"].map(_TX_LABELS).fillna(monthly_agg["transaction_type"])
                    fig_area = px.bar(
                        monthly_agg,
                        x="month",
                        y="amount",
                        color="label",
                        barmode="stack",
                        color_discrete_sequence=["#64FFDA", "#4FC3F7", "#81C784"],
                        labels={"amount": "R$", "month": "Mês", "label": "Tipo"},
                    )
                    fig_area.update_layout(**LAYOUT)
                    st.plotly_chart(fig_area, use_container_width=True)

                st.divider()

                # ── Receita por entidade ──────────────────────────────────────
                if "source_entity_name" in df_period.columns:
                    st.markdown('<span class="nx-section-label">Receita por entidade</span>', unsafe_allow_html=True)
                    by_entity = (
                        df_period.groupby("source_entity_name", as_index=False)["amount"]
                        .sum()
                        .sort_values("amount", ascending=False)
                    )
                    by_entity["pct"] = (by_entity["amount"] / total_income * 100).round(1)
                    fig_ent = px.bar(
                        by_entity,
                        x="source_entity_name",
                        y="amount",
                        text=[f"R$ {v:,.0f} ({p:.0f}%)" for v, p in zip(by_entity["amount"], by_entity["pct"])],
                        color_discrete_sequence=["#64FFDA"],
                        labels={"amount": "R$", "source_entity_name": "Entidade"},
                    )
                    fig_ent.update_traces(textposition="outside")
                    fig_ent.update_layout(**LAYOUT, showlegend=False, xaxis_title="")
                    st.plotly_chart(fig_ent, use_container_width=True)

        with st.expander("ℹ️ Como melhorar essa análise?", expanded=False):
            st.markdown("""
            Cadastre **fontes de renda nomeadas** na aba **⚙️ Gerenciar Fontes**.
            Quando você vincula uma transação a uma fonte específica (ex: "Salário Empresa X"),
            o sistema consegue mostrar o desempenho de cada fonte individualmente.

            Isso é especialmente útil para quem tem múltiplas empresas ou trabalha como freelancer
            e quer saber qual cliente gera mais receita.
            """)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GERENCIAR FONTES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_manage:
    if is_reader():
        st.info("🔒 Acesso somente leitura — você não tem permissão para adicionar ou desativar fontes de renda.")
        st.stop()

    if not entities:
        st.info(
            "📭 Nenhuma entidade cadastrada. Complete o perfil inicial para continuar."
        )
        if st.button("🚀 Configurar perfil", type="primary"):
            st.switch_page("pages/01_dashboard_geral.py")
        st.stop()

    st.markdown('<span class="nx-section-label">Adicionar fonte de renda</span>', unsafe_allow_html=True)

    entity_options = {f"{e['name']} ({e['type']})": e["id"] for e in entities}

    with st.form("form_income_source"):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            source_name = st.text_input(
                "Nome da fonte",
                placeholder="Ex: Salário Empresa X, Freelance Cliente Y",
            )
            source_type_label = st.selectbox(
                "Tipo de fonte",
                list(_SOURCE_LABELS.values()),
            )
        with col_s2:
            entity_label = st.selectbox("Entidade vinculada", list(entity_options.keys()))
            expected = st.number_input(
                "Valor mensal esperado (R$) — opcional",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                help="Estimativa do quanto esta fonte gera por mês",
            )

        adicionar = st.form_submit_button("➕ Adicionar fonte", type="primary")

        if adicionar and source_name.strip():
            source_type_value = next(
                k for k, v in _SOURCE_LABELS.items() if v == source_type_label
            )
            try:
                _catalog.create_income_source(
                    entity_id=entity_options[entity_label],
                    name=source_name.strip(),
                    source_type=source_type_value,
                    expected_monthly_amount=Decimal(str(expected)) if expected > 0 else None,
                )
                st.toast(f"Fonte '{source_name.strip()}' adicionada!", icon="🌱")
                _reload()
                st.rerun()
            except Exception as exc:
                st.error(f"Erro ao cadastrar: {exc}")
        elif adicionar:
            st.warning("Informe o nome da fonte de renda.")

    st.divider()

    # ── Lista de fontes ativa ─────────────────────────────────────────────────
    st.markdown('<span class="nx-section-label">Fontes cadastradas</span>', unsafe_allow_html=True)

    active_sources = [s for s in sources if s["is_active"]]

    if not active_sources:
        st.info("📭 Nenhuma fonte de renda cadastrada ainda. Use o formulário acima para adicionar.")
    else:
        entity_map = {e["id"]: f"{e['name']} ({e['type']})" for e in entities}
        for src in active_sources:
            col_name, col_type, col_entity, col_action = st.columns([3, 2, 3, 1])
            with col_name:
                st.markdown(f"**{src['name']}**")
            with col_type:
                st.caption(_SOURCE_LABELS.get(src["source_type"], src["source_type"]))
            with col_entity:
                st.caption(entity_map.get(src["entity_id"], "—"))
            with col_action:
                if st.button("🗑️", key=f"del_src_{src['id']}", help="Desativar esta fonte"):
                    try:
                        _catalog.deactivate_income_source(src["id"])
                        st.toast(f"'{src['name']}' desativada.", icon="🗑️")
                        _reload()
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
