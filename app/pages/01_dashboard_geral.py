import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.analytics.cashflow import pf_pj_flow
from src.analytics.kpis import monthly_net_result, period_comparison, pf_pj_kpis, revenue_expense_by_month
from src.analytics.loader import load_transactions_df
from src.analytics.pf_pj_analysis import summarize_pf_pj_direction
from app.ui import FAVICON_IMG,  page_header, plotly_layout, TYPE_COLORS, TIPO_LABEL, feather_icon
from app.export import generate_dashboard_pdf
from src.services.catalog_service import CatalogService

st.set_page_config(page_title="Visão Geral · Inside Money", layout="wide", page_icon=FAVICON_IMG or "📊")
def _render_onboarding() -> None:
    """Exibe wizard de configuração inicial de 4 etapas quando o banco está vazio."""
    catalog = CatalogService(owner_id=st.session_state.get("effective_owner_id"))
    existing_pf  = catalog.list_entities("PF")
    existing_pj  = catalog.list_entities("PJ")
    income_sources = catalog.list_income_sources() if existing_pf else []

    # ── Indicador de progresso visual ────────────────────────────────────────
    step_done   = feather_icon("check-circle", 20, "#64FFDA", "Concluído")
    step_active = feather_icon("clock", 20, "#FFD600", "Em andamento")
    step_todo   = feather_icon("circle", 20, "#8892B0", "Pendente")
    step1 = step_done if existing_pf   else step_active
    step2 = step_done if existing_pj   else (step_active if existing_pf   else step_todo)
    step3 = step_done if income_sources else (step_active if existing_pj or (existing_pf and not existing_pj) else step_todo)
    # Passo 4 fica disponível após completar os anteriores (PF obrigatório) 
    step4 = step_active if existing_pf else step_todo

    st.markdown(f"""
        <span style='vertical-align:middle;'>{feather_icon('user', 28, '#64FFDA', 'Bem-vindo')}</span>
        <span style='font-size:1.6rem;font-weight:700;margin-left:0.5rem;'>Bem-vindo ao Inside Money!</span>
    """, unsafe_allow_html=True)
    st.markdown(
        "Configure seu perfil em poucos passos para começar a entender suas finanças."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**{step1} Seu perfil**", unsafe_allow_html=True)
        st.caption("Quem é você?")
    with col2:
        st.markdown(f"**{step2} Sua empresa**", unsafe_allow_html=True)
        st.caption("Você tem CNPJ?")
    with col3:
        st.markdown(f"**{step3} Fontes de renda**", unsafe_allow_html=True)
        st.caption("De onde vem seu dinheiro?")
    with col4:
        st.markdown(f"**{step4} Primeiro dado**", unsafe_allow_html=True)
        st.caption("Importe ou registre")

    # Barra de progresso
    steps_done = sum([bool(existing_pf), bool(existing_pj or existing_pf), bool(income_sources)])
    st.progress(min(steps_done / 3, 1.0))

    st.divider()

    # ── Passo 1 — Perfil PF ──────────────────────────────────────────────────
    if not existing_pf:
        st.markdown("#### Passo 1 — Quem é você?")
        st.caption("Primeiro, precisamos saber seu nome para criar seu perfil pessoal.")
        with st.form("onboarding_pf"):
            nome = st.text_input("Seu nome completo", placeholder="Ex: João da Silva")
            if st.form_submit_button("Criar meu perfil", type="primary") and nome.strip():
                try:
                    catalog.create_entity(nome.strip(), "PF")
                    st.toast(f"Perfil '{nome.strip()}' criado!")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        return

    # ── Passo 2 — Empresa PJ ────────────────────────────────────────────────
    if not existing_pj and "onboarding_skip_pj" not in st.session_state:
        st.markdown("#### Passo 2 — Você tem empresa?")
        st.caption(
            "Se você é sócio, MEI ou tem CNPJ, adicione sua empresa. "
            "Isso permite separar seus gastos pessoais dos empresariais. "
            "*Pode pular se preferir.*"
        )
        with st.form("onboarding_pj"):
            nome_empresa = st.text_input("Nome da empresa", placeholder="Ex: Silva Consultoria Ltda")
            col_pj1, col_pj2 = st.columns([2, 1])
            with col_pj1:
                criar = st.form_submit_button("Adicionar empresa", type="primary")
            with col_pj2:
                pular = st.form_submit_button("Pular este passo")
            if criar and nome_empresa.strip():
                try:
                    catalog.create_entity(nome_empresa.strip(), "PJ")
                    st.toast(f"Empresa '{nome_empresa.strip()}' criada!")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            if pular:
                st.session_state["onboarding_skip_pj"] = True
                st.rerun()
        return

    # ── Passo 3 — Fontes de renda ────────────────────────────────────────────
    if not income_sources:
        from src.domain.enums import IncomeSourceType
        _SOURCE_LABELS = {
            IncomeSourceType.SALARIO:      "Salário (CLT)",
            IncomeSourceType.FREELANCE:    "Freelance / Autônomo",
            IncomeSourceType.DIVIDENDOS:   "Dividendos da empresa",
            IncomeSourceType.PRO_LABORE:   "Pró-labore",
            IncomeSourceType.INVESTIMENTO: "Investimentos",
            IncomeSourceType.ALUGUEL:      "Aluguel",
            IncomeSourceType.OUTRO:        "Outra fonte",
        }
        entity_options = {e.name: e.id for e in (existing_pf + existing_pj)}

        st.markdown("#### Passo 3 — De onde vem seu dinheiro?")
        st.caption(
            "Adicione suas fontes de renda (salário, freelance, dividendos…). "
            "Isso torna suas análises muito mais precisas."
        )
        with st.form("onboarding_income_source"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                source_name = st.text_input("Nome da fonte", placeholder="Ex: Salário Empresa X")
                source_type_label = st.selectbox("Tipo", list(_SOURCE_LABELS.values()))
            with col_s2:
                entity_name_sel = st.selectbox("De qual entidade?", list(entity_options.keys()))
                expected = st.number_input(
                    "Valor mensal esperado (R$) — opcional",
                    min_value=0.0, step=100.0, format="%.2f",
                )
            col_s3, col_s4 = st.columns([2, 1])
            with col_s3:
                adicionar = st.form_submit_button("Adicionar fonte de renda", type="primary")
            with col_s4:
                pular_fonte = st.form_submit_button("Pular este passo")

            if adicionar and source_name.strip():
                from decimal import Decimal
                source_type_value = next(
                    k for k, v in _SOURCE_LABELS.items() if v == source_type_label
                )
                try:
                    catalog.create_income_source(
                        entity_id=entity_options[entity_name_sel],
                        name=source_name.strip(),
                        source_type=source_type_value.value,
                        expected_monthly_amount=Decimal(str(expected)) if expected > 0 else None,
                    )
                    st.toast(f"Fonte '{source_name.strip()}' adicionada!")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
            if pular_fonte:
                st.session_state["onboarding_skip_source"] = True
                st.rerun()
        return

    # ── Passo 4 — Primeiro dado ───────────────────────────────────────────────
    st.markdown("#### 🎉 Tudo pronto! Agora é só adicionar seus dados.")
    st.success(
        "Perfil configurado com sucesso. Importe um extrato bancário ou "
        "registre sua primeira transação para começar a visualizar suas finanças."
    )
    col_p1, col_p2, _ = st.columns([2, 2, 4])
    with col_p1:
        if st.button("Importar extrato", type="primary"):
            st.switch_page("pages/05_importacao_dados.py")
    with col_p2:
        if st.button("Registrar transação"):
            st.switch_page("pages/07_novo_lancamento.py")


@st.cache_data(ttl=30)
def _get_data(owner_id: int | None):
    return load_transactions_df(owner_id=owner_id)


@st.cache_data(ttl=30)
def _get_flow(owner_id: int | None):
    return pf_pj_flow(load_transactions_df(owner_id=owner_id))


@st.cache_data(ttl=30)
def _get_aportes(owner_id: int | None):
    df_all = load_transactions_df(owner_id=owner_id)
    return df_all[df_all["transaction_type"].isin({"aporte_pf_pj", "emprestimo_pf_pj"})].copy()


is_dark = page_header("Visão Geral", "Como estão suas finanças este mês")
LAYOUT = plotly_layout(is_dark)

_uid = st.session_state.get("effective_owner_id")
df = _get_data(_uid)

if df.empty:
    _render_onboarding()
    st.stop()

# ── Tabs principais ───────────────────────────────────────────────────────────
tab_resumo, tab_transf, tab_aportes = st.tabs(
    ["Resumo Financeiro", "Transferências PF↔PJ", "Aportes na Empresa"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESUMO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_resumo:
    # ── Indicadores principais ────────────────────────────────────────────────
    kpis = pf_pj_kpis(df)

    _months = sorted(df["date"].dt.to_period("M").astype(str).unique())
    _comparison: dict | None = None
    if len(_months) >= 2:
        _comparison = period_comparison(df, _months[-1], _months[-2])

    def _delta(key: str, invert: bool = False) -> str | None:
        """Retorna string de delta percentual formatada, ou None se não disponível."""
        if _comparison is None:
            return None
        pct = _comparison[key]
        if invert:
            pct = -pct
        return f"{pct:+.1f}% vs {_months[-2]}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total recebido pela PJ",  f"R$ {kpis['pj_income']:,.2f}", delta=_delta("income_delta_pct"))
    c2.metric("Total recebido pela PF",  f"R$ {kpis['pf_income']:,.2f}")
    c3.metric("Total de despesas",       f"R$ {kpis['expenses']:,.2f}", delta=_delta("expense_delta_pct", invert=True), delta_color="inverse")
    c4.metric(
        "Saldo do período",
        f"R$ {kpis['balance']:,.2f}",
        delta=_delta("net_delta_pct"),
        delta_color="normal",
    )

    st.divider()

    # ── Participação das empresas + Resultado mensal ──────────────────────────
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

    # ── Evolução temporal: Receitas vs Despesas ───────────────────────────────
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

    # ── Fluxo PF ↔ PJ ─────────────────────────────────────────────────────────
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

    # ── Últimos 10 lançamentos ────────────────────────────────────────────────
    st.markdown('<span class="nx-section-label">Atividade Recente — Últimos 10 Lançamentos</span>', unsafe_allow_html=True)
    _COL_MAP = {
        "date":               "Data",
        "descricao":          "Descrição",
        "category":           "Categoria",
        "source_entity_type": "Origem",
        "amount":             "Valor (R$)",
    }
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

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TRANSFERÊNCIAS PF↔PJ
# ═══════════════════════════════════════════════════════════════════════════════
with tab_transf:
    df_flow = _get_flow(_uid)

    if df_flow.empty:
        st.info(
            "Nenhum fluxo entre você e sua empresa ainda. "
            "Registre uma transferência, aporte ou distribuição de dividendos para visualizar esta aba."
        )
        col_a, col_b, _ = st.columns([2, 2, 4])
        with col_a:
            if st.button("Registrar transação", type="primary", key="transf_reg"):
                st.switch_page("pages/07_novo_lancamento.py")
        with col_b:
            if st.button("Importar extrato", key="transf_imp"):
                st.switch_page("pages/05_importacao_dados.py")
    else:
        summary = summarize_pf_pj_direction(df_flow)
        pf_to_pj = float(summary.loc[summary["direction"] == "pf_to_pj", "amount"].values[0])
        pj_to_pf = float(summary.loc[summary["direction"] == "pj_to_pf", "amount"].values[0])

        tc1, tc2, tc3 = st.columns(3)
        tc1.metric("PF → PJ (aportes / empréstimos)", f"R$ {pf_to_pj:,.2f}")
        tc2.metric("PJ → PF (retiradas / dividendos)", f"R$ {pj_to_pf:,.2f}")
        tc3.metric("Saldo retornado à PF", f"R$ {pj_to_pf - pf_to_pj:,.2f}")

        with st.expander("O que significam esses tipos de fluxo?", expanded=False):
            st.markdown("""
            **Aporte PF → PJ** — dinheiro que você colocou na empresa como capital próprio (investimento).

            **Empréstimo PF → PJ** — valor que você emprestou para a empresa com intenção de receber de volta.

            **Transferência PF → PJ** — movimentação genérica de dinheiro da sua conta pessoal para a empresa.

            **Pró-labore** — remuneração mensal que você recebe da empresa como sócio-administrador.

            **Dividendos** — distribuição dos lucros da empresa para os sócios. Em geral isento de IR para PF.

            **Saldo retornado** — quanto a empresa já te devolveu em relação ao que você colocou.
            """)

        st.divider()

        st.markdown('<span class="nx-section-label">Volume por Tipo de Fluxo</span>', unsafe_allow_html=True)
        by_type = (
            df_flow.groupby("transaction_type", as_index=False)["amount"]
            .sum()
            .sort_values("amount", ascending=False)
        )
        by_type["label"] = by_type["transaction_type"].map(TIPO_LABEL).fillna(by_type["transaction_type"])
        by_type["cor"]   = by_type["transaction_type"].map(TYPE_COLORS)
        fig_bt = px.bar(
            by_type,
            x="label",
            y="amount",
            color="label",
            color_discrete_map=dict(zip(by_type["label"], by_type["cor"])),
            text=[f"R$ {v:,.0f}" for v in by_type["amount"]],
            labels={"amount": "R$", "label": "Tipo"},
        )
        fig_bt.update_traces(textposition="outside")
        fig_bt.update_layout(**LAYOUT, showlegend=False, xaxis_title="")
        st.plotly_chart(fig_bt, use_container_width=True)

        st.divider()

        st.markdown('<span class="nx-section-label">Evolução Mensal por Tipo</span>', unsafe_allow_html=True)
        df_flow_plot = df_flow.copy()
        df_flow_plot["month"] = df_flow_plot["date"].dt.to_period("M").astype(str)
        monthly_flow = (
            df_flow_plot.groupby(["month", "transaction_type"], as_index=False)["amount"]
            .sum()
            .sort_values("month")
        )
        monthly_flow["label"] = monthly_flow["transaction_type"].map(TIPO_LABEL).fillna(monthly_flow["transaction_type"])
        fig_mf = px.bar(
            monthly_flow,
            x="month",
            y="amount",
            color="label",
            barmode="group",
            color_discrete_sequence=["#64FFDA", "#4FC3F7", "#81C784", "#FFB74D", "#CE93D8", "#FFF176"],
            labels={"amount": "R$", "month": "Mês", "label": "Tipo"},
        )
        fig_mf.update_layout(**LAYOUT)
        st.plotly_chart(fig_mf, use_container_width=True)

        st.divider()

        st.markdown('<span class="nx-section-label">Transações de Fluxo</span>', unsafe_allow_html=True)
        _FLOW_COLS = ["date", "transaction_type", "source_entity_name", "destination_entity_name", "amount", "currency"]
        flow_cols_present = [c for c in _FLOW_COLS if c in df_flow.columns]
        st.dataframe(df_flow[flow_cols_present], use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — APORTES NA EMPRESA
# ═══════════════════════════════════════════════════════════════════════════════
with tab_aportes:
    df_aportes = _get_aportes(_uid)

    if df_aportes.empty:
        st.info(
            "Nenhum aporte ou empréstimo da sua parte para a empresa ainda. "
            "Registre um aporte de capital ou empréstimo para visualizar esta aba."
        )
        col_a, col_b, _ = st.columns([2, 2, 4])
        with col_a:
            if st.button("Registrar aporte", type="primary", key="ap_reg"):
                st.switch_page("pages/07_novo_lancamento.py")
        with col_b:
            if st.button("Importar extrato", key="ap_imp"):
                st.switch_page("pages/05_importacao_dados.py")
    else:
        total_aportes     = float(df_aportes.loc[df_aportes["transaction_type"] == "aporte_pf_pj",    "amount"].sum())
        total_emprestimos = float(df_aportes.loc[df_aportes["transaction_type"] == "emprestimo_pf_pj", "amount"].sum())

        ac1, ac2, ac3 = st.columns(3)
        ac1.metric("Aportes",          f"R$ {total_aportes:,.2f}")
        ac2.metric("Empréstimos",       f"R$ {total_emprestimos:,.2f}")
        ac3.metric("Total Investido", f"R$ {total_aportes + total_emprestimos:,.2f}")

        with st.expander("Aporte vs Empréstimo — qual a diferença?", expanded=False):
            st.markdown("""
            **Aporte de capital** — você coloca dinheiro na empresa como investimento permanente.
            Esse valor aumenta o patrimônio líquido da empresa e não precisa ser devolvido.

            **Empréstimo PF → PJ** — você empresta dinheiro para a empresa com a intenção de receber de volta.
            A empresa registra como dívida (passivo) e você como crédito a receber.

            **Dica:** Formalize empréstimos em contrato assinado para evitar questionamentos fiscais.
            """)

        st.divider()

        st.markdown('<span class="nx-section-label">Evolução Temporal</span>', unsafe_allow_html=True)
        df_ap_plot = df_aportes.copy()
        df_ap_plot["month"] = df_ap_plot["date"].dt.to_period("M").astype(str)
        monthly_ap = (
            df_ap_plot.groupby(["month", "transaction_type"], as_index=False)["amount"]
            .sum()
            .sort_values("month")
        )
        monthly_ap["label"] = monthly_ap["transaction_type"].map(TIPO_LABEL).fillna(monthly_ap["transaction_type"])
        fig_ap = px.bar(
            monthly_ap,
            x="month",
            y="amount",
            color="label",
            barmode="group",
            color_discrete_map={"Aporte PF→PJ": TYPE_COLORS["aporte_pf_pj"], "Empréstimo PF→PJ": TYPE_COLORS["emprestimo_pf_pj"]},
            labels={"amount": "R$", "month": "Mês", "label": "Tipo"},
        )
        fig_ap.update_layout(**LAYOUT)
        st.plotly_chart(fig_ap, use_container_width=True)

        st.divider()

        st.markdown('<span class="nx-section-label">Transações</span>', unsafe_allow_html=True)
        _AP_COLS = ["date", "transaction_type", "source_entity_name", "destination_entity_name", "amount", "currency", "description"]
        ap_cols_present = [c for c in _AP_COLS if c in df_aportes.columns]
        st.dataframe(df_aportes[ap_cols_present], use_container_width=True, hide_index=True)

