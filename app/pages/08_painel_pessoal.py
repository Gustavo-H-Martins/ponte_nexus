from decimal import Decimal
import streamlit as st
import pandas as pd
import plotly.express as px

from src.analytics.kpis import top_expense_categories
from src.analytics.loader import load_transactions_df
from src.domain.enums import IncomeSourceType
from src.services.catalog_service import CatalogService
from app.ui import page_header, plotly_layout, TYPE_COLORS, TIPO_LABEL

st.set_page_config(
    page_title="Painel Pessoal · Ponte Nexus", layout="wide", page_icon="�"
)

_PF_INCOME_TYPES = {"pro_labore", "dividendos"}
_TIPOS_RENDA = {"pro_labore", "dividendos"}

_SOURCE_LABELS: dict[str, str] = {
    IncomeSourceType.SALARIO.value:      "Salário (CLT)",
    IncomeSourceType.FREELANCE.value:    "Freelance / Autônomo",
    IncomeSourceType.DIVIDENDOS.value:   "Dividendos da empresa",
    IncomeSourceType.PRO_LABORE.value:   "Pró-labore",
    IncomeSourceType.INVESTIMENTO.value: "Investimentos",
    IncomeSourceType.ALUGUEL.value:      "Aluguel",
    IncomeSourceType.OUTRO.value:        "Outra fonte",
}


@st.cache_data(ttl=30)
def _get_data(owner_id: int | None):
    return load_transactions_df(owner_id=owner_id)


@st.cache_data(ttl=30)
def _get_entities(owner_id: int | None) -> list[dict]:
    catalog = CatalogService(owner_id=owner_id)
    return [{"id": e.id, "name": e.name, "type": e.entity_type} for e in catalog.list_entities()]


@st.cache_data(ttl=30)
def _get_sources(owner_id: int | None) -> list[dict]:
    catalog = CatalogService(owner_id=owner_id)
    return [
        {"id": s.id, "name": s.name, "source_type": s.source_type, "entity_id": s.entity_id, "is_active": s.is_active}
        for s in catalog.list_income_sources()
    ]


def _reload_fontes() -> None:
    _get_entities.clear()
    _get_sources.clear()


is_dark = page_header(
    "Meu Bolso",
    "Sua vida financeira pessoal em um lugar só",
)
LAYOUT = plotly_layout(is_dark)

df_all = _get_data(st.session_state.get("effective_owner_id"))

if df_all.empty:
    st.info(
        "💭 Nenhuma transação encontrada. Importe seu extrato ou registre seus pró-labores e dividendos."
    )
    col_a, col_b, _ = st.columns([2, 2, 4])
    with col_a:
        if st.button("📂 Importar extrato", type="primary"):
            st.switch_page("pages/05_importacao_dados.py")
    with col_b:
        if st.button("✏️ Registrar transação"):
            st.switch_page("pages/07_novo_lancamento.py")
    st.stop()

# ── Tabs principais ───────────────────────────────────────────────────────────
tab_bolso, tab_remuneracao, tab_fontes = st.tabs(
    ["💼 Meu Bolso", "💰 Remuneração", "🌱 Fontes de Renda"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MEU BOLSO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_bolso:
    # ── Seletor de mês de referência ──────────────────────────────────────────
    available_months = sorted(
        df_all["date"].dt.to_period("M").astype(str).unique().tolist(), reverse=True
    )

    selected_month = st.selectbox("Mês de referência", options=available_months, index=0)

    # ── Dados filtrados pelo mês selecionado ──────────────────────────────────────
    df_month = df_all[
        df_all["date"].dt.to_period("M").astype(str) == selected_month
    ].copy()

    df_pf_income = df_month[df_month["transaction_type"].isin(_PF_INCOME_TYPES)]
    df_pf_expense = df_month[
        (df_month["transaction_type"] == "despesa")
        & (df_month["source_entity_type"] == "PF")
    ]

    total_recebido = float(df_pf_income["amount"].sum())
    total_despesa = float(df_pf_expense["amount"].sum())
    saldo_pessoal = total_recebido - total_despesa

    # ── Deltas vs mês anterior ────────────────────────────────────────────────────
    idx = available_months.index(selected_month)
    delta_recebido: str | None = None
    delta_despesa: str | None = None

    if idx + 1 < len(available_months):
        prev_month = available_months[idx + 1]
        df_prev = df_all[df_all["date"].dt.to_period("M").astype(str) == prev_month]

        prev_income = float(df_prev[df_prev["transaction_type"].isin(_PF_INCOME_TYPES)]["amount"].sum())
        prev_expense = float(
            df_prev[
                (df_prev["transaction_type"] == "despesa")
                & (df_prev["source_entity_type"] == "PF")
            ]["amount"].sum()
        )

        if prev_income > 0:
            delta_recebido = f"{(total_recebido - prev_income) / prev_income * 100:+.1f}% vs {prev_month}"
        if prev_expense > 0:
            delta_despesa = f"{(total_despesa - prev_expense) / prev_expense * 100:+.1f}% vs {prev_month}"

    # ── KPIs pessoais ─────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Recebido (PF)", f"R$ {total_recebido:,.2f}", delta=delta_recebido)
    c2.metric(
        "📉 Despesas Pessoais",
        f"R$ {total_despesa:,.2f}",
        delta=delta_despesa,
        delta_color="inverse",
    )
    c3.metric("⚖️ Saldo Pessoal", f"R$ {saldo_pessoal:,.2f}")

    st.divider()

    # ── Receita PF acumulada por mês (área) ───────────────────────────────────────
    st.markdown(
        '<span class="nx-section-label">Receita Pessoal — Histórico Mensal</span>',
        unsafe_allow_html=True,
    )
    df_pf_all_income = df_all[df_all["transaction_type"].isin(_PF_INCOME_TYPES)].copy()

    if df_pf_all_income.empty:
        st.info("Nenhum registro de pró-labore ou dividendos no histórico.")
    else:
        df_pf_all_income["month"] = df_pf_all_income["date"].dt.to_period("M").astype(str)
        monthly_income = (
            df_pf_all_income.groupby(["month", "transaction_type"], as_index=False)["amount"]
            .sum()
            .sort_values("month")
        )
        monthly_income["label"] = monthly_income["transaction_type"].map(
            {"pro_labore": "Pró-Labore", "dividendos": "Dividendos"}
        )
        fig_area = px.area(
            monthly_income,
            x="month",
            y="amount",
            color="label",
            color_discrete_map={
                "Pró-Labore": TYPE_COLORS["pro_labore"],
                "Dividendos": TYPE_COLORS["dividendos"],
            },
            markers=True,
            labels={"amount": "R$", "month": "Mês", "label": "Fonte"},
        )
        fig_area.update_layout(**LAYOUT)
        st.plotly_chart(fig_area, use_container_width=True)

    st.divider()

    # ── Top despesas PF + Composição da renda ─────────────────────────────────────
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown(
            '<span class="nx-section-label">Top 5 Categorias de Despesa (mês)</span>',
            unsafe_allow_html=True,
        )
        if df_pf_expense.empty:
            st.info("Nenhuma despesa pessoal no período selecionado.")
        else:
            top5 = top_expense_categories(df_pf_expense, n=5)
            fig_top = px.bar(
                top5,
                x="amount",
                y="category",
                orientation="h",
                text=[f"R$ {v:,.0f}" for v in top5["amount"]],
                color_discrete_sequence=["#FF6B6B"],
                labels={"amount": "R$", "category": "Categoria"},
            )
            fig_top.update_traces(textposition="outside")
            fig_top.update_layout(
                **LAYOUT,
                showlegend=False,
                yaxis={"categoryorder": "total ascending"},
            )
            st.plotly_chart(fig_top, use_container_width=True)

    with col_right:
        st.markdown(
            '<span class="nx-section-label">Composição da Renda PF (mês)</span>',
            unsafe_allow_html=True,
        )
        if df_pf_income.empty:
            st.info("Nenhuma receita pessoal no período selecionado.")
        else:
            by_type = df_pf_income.groupby("transaction_type", as_index=False)["amount"].sum()
            by_type["label"] = by_type["transaction_type"].map(
                {"pro_labore": "Pró-Labore", "dividendos": "Dividendos"}
            )
            fig_pie = px.pie(
                by_type,
                names="label",
                values="amount",
                hole=0.45,
                color="label",
                color_discrete_map={
                    "Pró-Labore": TYPE_COLORS["pro_labore"],
                    "Dividendos": TYPE_COLORS["dividendos"],
                },
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(**LAYOUT, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # ── Receitas × Despesas — Últimos 6 meses ─────────────────────────────────────
    st.markdown(
        '<span class="nx-section-label">Receitas × Despesas — Últimos 6 Meses</span>',
        unsafe_allow_html=True,
    )

    _months_all = sorted(
        df_all["date"].dt.to_period("M").astype(str).unique().tolist()
    )
    _months_6 = _months_all[-6:]

    df_6m = df_all[df_all["date"].dt.to_period("M").astype(str).isin(_months_6)].copy()
    df_6m["month"] = df_6m["date"].dt.to_period("M").astype(str)

    _income_6 = (
        df_6m[df_6m["transaction_type"].isin(_PF_INCOME_TYPES)]
        .groupby("month")["amount"]
        .sum()
        .reindex(_months_6, fill_value=0)
    )
    _expense_6 = (
        df_6m[
            (df_6m["transaction_type"] == "despesa")
            & (df_6m["source_entity_type"] == "PF")
        ]
        .groupby("month")["amount"]
        .sum()
        .reindex(_months_6, fill_value=0)
    )

    _df_flow = (
        pd.DataFrame({"Receita PF": _income_6, "Despesa PF": _expense_6})
        .reset_index()
        .rename(columns={"month": "Mês"})
        .melt(id_vars="Mês", var_name="Tipo", value_name="R$")
    )

    fig_flow = px.bar(
        _df_flow,
        x="Mês",
        y="R$",
        color="Tipo",
        barmode="group",
        color_discrete_map={"Receita PF": "#64FFDA", "Despesa PF": "#FF6B6B"},
        text_auto=".2s",
        labels={"R$": "Valor (R$)", "Mês": ""},
    )
    fig_flow.update_layout(**LAYOUT)
    st.plotly_chart(fig_flow, use_container_width=True)

    st.divider()

    # ── Últimos lançamentos pessoais ───────────────────────────────────────────────
    st.markdown(
        '<span class="nx-section-label">Últimos Lançamentos Pessoais</span>',
        unsafe_allow_html=True,
    )

    df_recent = df_all[
        df_all["transaction_type"].isin(_PF_INCOME_TYPES)
        | (df_all["source_entity_type"] == "PF")
    ].copy()
    df_recent = df_recent.sort_values("date", ascending=False).head(10)

    if df_recent.empty:
        st.info("Nenhum lançamento pessoal encontrado.")
    else:
        _REC_COL_MAP = {
            "date":             "Data",
            "transaction_type": "Tipo",
            "description":      "Descrição",
            "category":         "Categoria",
            "amount":           "Valor (R$)",
        }
        _cols_ok = [c for c in _REC_COL_MAP if c in df_recent.columns]
        df_rec_disp = df_recent[_cols_ok].copy().rename(columns=_REC_COL_MAP)

        if "Data" in df_rec_disp.columns:
            df_rec_disp["Data"] = df_rec_disp["Data"].dt.strftime("%d/%m/%Y")
        if "Tipo" in df_rec_disp.columns:
            df_rec_disp["Tipo"] = df_rec_disp["Tipo"].map(TIPO_LABEL).fillna(df_rec_disp["Tipo"])
        if "Valor (R$)" in df_rec_disp.columns:
            df_rec_disp["Valor (R$)"] = df_rec_disp["Valor (R$)"].map("R$ {:,.2f}".format)

        st.dataframe(df_rec_disp, use_container_width=True, hide_index=True)

        if st.button("📋 Ver extrato completo", type="primary"):
            st.switch_page("pages/06_lancamentos.py")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REMUNERAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_remuneracao:
    df_rem = df_all[df_all["transaction_type"].isin(_TIPOS_RENDA)].copy()

    if df_rem.empty:
        st.info(
            "💭 Nenhum pró-labore ou dividendo registrado ainda. "
            "Esses valores aparecem aqui quando você registra retiradas da empresa."
        )
        col_ra, col_rb, _ = st.columns([2, 2, 4])
        with col_ra:
            if st.button("✏️ Registrar retirada", type="primary", key="rem_reg"):
                st.switch_page("pages/07_novo_lancamento.py")
        with col_rb:
            if st.button("📂 Importar extrato", key="rem_imp"):
                st.switch_page("pages/05_importacao_dados.py")
    else:
        total_pro_labore = float(df_rem.loc[df_rem["transaction_type"] == "pro_labore", "amount"].sum())
        total_dividendos  = float(df_rem.loc[df_rem["transaction_type"] == "dividendos", "amount"].sum())

        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("💼 Pró-Labore",        f"R$ {total_pro_labore:,.2f}")
        rc2.metric("💰 Dividendos",         f"R$ {total_dividendos:,.2f}")
        rc3.metric("∑ Total Distribuído", f"R$ {total_pro_labore + total_dividendos:,.2f}")

        with st.expander("ℹ️ Pró-labore vs Dividendos — qual a diferença?", expanded=False):
            st.markdown("""
            **Pró-labore** é a remuneração mensal do sócio pelo trabalho que realiza na empresa.
            Tem incidência de INSS e IRPF. É uma despesa dedutível da empresa.

            **Dividendos** são a distribuição dos lucros da empresa aos sócios.
            Atualmente isentos de IR para pessoa física na maioria dos casos.
            Dependem de que a empresa tenha lucro contabil apurado.

            **Dica:** Consulte seu contador para definir a proporção ideal para sua situação.
            """)

        st.divider()

        rem_left, rem_right = st.columns(2, gap="large")

        with rem_left:
            st.markdown('<span class="nx-section-label">Proporção Pró-Labore vs Dividendos</span>', unsafe_allow_html=True)
            by_type_rem = df_rem.groupby("transaction_type", as_index=False)["amount"].sum()
            by_type_rem["label"] = by_type_rem["transaction_type"].map(TIPO_LABEL).fillna(by_type_rem["transaction_type"])
            fig_rem_pie = px.pie(
                by_type_rem,
                names="label",
                values="amount",
                hole=0.45,
                color="label",
                color_discrete_map={"Pró-Labore": TYPE_COLORS["pro_labore"], "Dividendos": TYPE_COLORS["dividendos"]},
            )
            fig_rem_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_rem_pie.update_layout(**LAYOUT, showlegend=False)
            st.plotly_chart(fig_rem_pie, use_container_width=True)

        with rem_right:
            st.markdown('<span class="nx-section-label">Evolução Mensal</span>', unsafe_allow_html=True)
            df_rem_plot = df_rem.copy()
            df_rem_plot["month"] = df_rem_plot["date"].dt.to_period("M").astype(str)
            monthly_rem = (
                df_rem_plot.groupby(["month", "transaction_type"], as_index=False)["amount"]
                .sum()
                .sort_values("month")
            )
            monthly_rem["label"] = monthly_rem["transaction_type"].map(TIPO_LABEL).fillna(monthly_rem["transaction_type"])
            fig_rem_bar = px.bar(
                monthly_rem,
                x="month",
                y="amount",
                color="label",
                barmode="group",
                color_discrete_map={"Pró-Labore": TYPE_COLORS["pro_labore"], "Dividendos": TYPE_COLORS["dividendos"]},
                labels={"amount": "R$", "month": "Mês", "label": "Tipo"},
            )
            fig_rem_bar.update_layout(**LAYOUT)
            st.plotly_chart(fig_rem_bar, use_container_width=True)

        st.divider()
        st.markdown('<span class="nx-section-label">Registros</span>', unsafe_allow_html=True)
        _REM_COLS = ["date", "transaction_type", "source_entity_name", "destination_entity_name", "amount", "currency"]
        rem_cols_present = [c for c in _REM_COLS if c in df_rem.columns]
        st.dataframe(df_rem[rem_cols_present], use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FONTES DE RENDA
# ═══════════════════════════════════════════════════════════════════════════════
with tab_fontes:
    entities = _get_entities(st.session_state.get("effective_owner_id"))
    sources  = _get_sources(st.session_state.get("effective_owner_id"))
    _INCOME_TX_TYPES = {"receita", "pro_labore", "dividendos"}

    subtab_analysis, subtab_manage = st.tabs(["📊 Análise por Fonte", "⚙️ Gerenciar Fontes"])

    with subtab_analysis:
        if df_all.empty:
            st.info("📭 Nenhuma transação encontrada. Importe ou registre dados para visualizar a análise.")
        else:
            df_income = df_all[df_all["transaction_type"].isin(_INCOME_TX_TYPES)].copy()

            if df_income.empty:
                st.info(
                    "📭 Nenhuma receita encontrada. "
                    "Registre receitas, pró-labore ou dividendos para ver a análise."
                )
            else:
                available_months_f = sorted(
                    df_income["date"].dt.to_period("M").astype(str).unique().tolist()
                )
                col_f1, col_f2, _ = st.columns([2, 2, 4])
                with col_f1:
                    period_start = st.selectbox("De", available_months_f, index=0, key="f_start")
                with col_f2:
                    period_end = st.selectbox("Até", available_months_f, index=len(available_months_f) - 1, key="f_end")

                mask_f = (
                    (df_income["date"].dt.to_period("M").astype(str) >= period_start)
                    & (df_income["date"].dt.to_period("M").astype(str) <= period_end)
                )
                df_period = df_income[mask_f].copy()

                if df_period.empty:
                    st.info("Nenhuma receita no período selecionado.")
                else:
                    total_income = float(df_period["amount"].sum())

                    col_k1, col_k2, col_k3 = st.columns(3)
                    col_k1.metric("💰 Total de receitas", f"R$ {total_income:,.2f}")
                    col_k2.metric("📅 Meses analisados", str(len(available_months_f)))
                    col_k3.metric("📊 Média mensal", f"R$ {total_income / max(len(available_months_f), 1):,.2f}")

                    st.divider()

                    st.markdown('<span class="nx-section-label">Receita por tipo</span>', unsafe_allow_html=True)
                    by_type_f = (
                        df_period.groupby("transaction_type", as_index=False)["amount"]
                        .sum()
                        .sort_values("amount", ascending=False)
                    )
                    _TX_LABELS = {"receita": "Receitas gerais", "pro_labore": "Pró-labore", "dividendos": "Dividendos"}
                    by_type_f["label"] = by_type_f["transaction_type"].map(_TX_LABELS).fillna(by_type_f["transaction_type"])

                    col_pie_f, col_bar_f = st.columns(2, gap="large")
                    with col_pie_f:
                        fig_pie_f = px.pie(
                            by_type_f, names="label", values="amount", hole=0.45,
                            color_discrete_sequence=["#64FFDA", "#4FC3F7", "#81C784", "#FFB74D"],
                        )
                        fig_pie_f.update_traces(textposition="inside", textinfo="percent+label")
                        fig_pie_f.update_layout(**LAYOUT, showlegend=False)
                        st.plotly_chart(fig_pie_f, use_container_width=True)

                    with col_bar_f:
                        df_monthly_f = df_period.copy()
                        df_monthly_f["month"] = df_monthly_f["date"].dt.to_period("M").astype(str)
                        monthly_agg_f = (
                            df_monthly_f.groupby(["month", "transaction_type"], as_index=False)["amount"]
                            .sum().sort_values("month")
                        )
                        monthly_agg_f["label"] = monthly_agg_f["transaction_type"].map(_TX_LABELS).fillna(monthly_agg_f["transaction_type"])
                        fig_area_f = px.bar(
                            monthly_agg_f, x="month", y="amount", color="label", barmode="stack",
                            color_discrete_sequence=["#64FFDA", "#4FC3F7", "#81C784"],
                            labels={"amount": "R$", "month": "Mês", "label": "Tipo"},
                        )
                        fig_area_f.update_layout(**LAYOUT)
                        st.plotly_chart(fig_area_f, use_container_width=True)

                    if "source_entity_name" in df_period.columns:
                        st.divider()
                        st.markdown('<span class="nx-section-label">Receita por entidade</span>', unsafe_allow_html=True)
                        by_entity_f = (
                            df_period.groupby("source_entity_name", as_index=False)["amount"]
                            .sum().sort_values("amount", ascending=False)
                        )
                        by_entity_f["pct"] = (by_entity_f["amount"] / total_income * 100).round(1)
                        fig_ent_f = px.bar(
                            by_entity_f,
                            x="source_entity_name",
                            y="amount",
                            text=[f"R$ {v:,.0f} ({p:.0f}%)" for v, p in zip(by_entity_f["amount"], by_entity_f["pct"])],
                            color_discrete_sequence=["#64FFDA"],
                            labels={"amount": "R$", "source_entity_name": "Entidade"},
                        )
                        fig_ent_f.update_traces(textposition="outside")
                        fig_ent_f.update_layout(**LAYOUT, showlegend=False, xaxis_title="")
                        st.plotly_chart(fig_ent_f, use_container_width=True)

    with subtab_manage:
        if not entities:
            st.info("📭 Nenhuma entidade cadastrada. Complete o perfil inicial para continuar.")
            if st.button("🚀 Configurar perfil", type="primary", key="fontes_config"):
                st.switch_page("pages/01_dashboard_geral.py")
        else:
            st.markdown('<span class="nx-section-label">Adicionar fonte de renda</span>', unsafe_allow_html=True)
            entity_options = {f"{e['name']} ({e['type']})": e["id"] for e in entities}

            with st.form("form_income_source_bolso"):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    source_name = st.text_input("Nome da fonte", placeholder="Ex: Salário Empresa X")
                    source_type_label = st.selectbox("Tipo de fonte", list(_SOURCE_LABELS.values()))
                with col_s2:
                    entity_label = st.selectbox("Entidade vinculada", list(entity_options.keys()))
                    expected = st.number_input(
                        "Valor mensal esperado (R$) — opcional",
                        min_value=0.0, step=100.0, format="%.2f",
                    )
                adicionar = st.form_submit_button("➕ Adicionar fonte", type="primary")

                if adicionar and source_name.strip():
                    source_type_value = next(
                        (k for k, v in _SOURCE_LABELS.items() if v == source_type_label), None
                    )
                    if source_type_value:
                        catalog_svc = CatalogService(owner_id=st.session_state.get("effective_owner_id"))
                        try:
                            catalog_svc.create_income_source(
                                entity_id=entity_options[entity_label],
                                name=source_name.strip(),
                                source_type=source_type_value,
                                expected_monthly_amount=Decimal(str(expected)) if expected > 0 else None,
                            )
                            st.toast(f"Fonte '{source_name.strip()}' adicionada!", icon="🌱")
                            _reload_fontes()
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

            if sources:
                st.divider()
                st.markdown('<span class="nx-section-label">Fontes cadastradas</span>', unsafe_allow_html=True)
                for s in sources:
                    col_s, col_status = st.columns([5, 1])
                    with col_s:
                        label = _SOURCE_LABELS.get(s["source_type"], s["source_type"])
                        st.markdown(f"**{s['name']}** — {label}")
                    with col_status:
                        status = "✅ Ativa" if s["is_active"] else "⏸ Inativa"
                        st.caption(status)

