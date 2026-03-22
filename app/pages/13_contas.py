from decimal import Decimal

import plotly.express as px
import streamlit as st

from app.ui import FAVICON_IMG,  page_header, is_reader, plotly_layout
from src.analytics.kpis import balance_history_by_account
from src.analytics.loader import load_transactions_df
from src.domain.enums import AccountType
from src.services.catalog_service import CatalogService


@st.cache_data(ttl=30)
def _get_balance_history(owner_id: int | None):
    return balance_history_by_account(load_transactions_df(owner_id=owner_id))


def _fmt_balance(value: Decimal, currency: str = "BRL") -> str:
    """Formata saldo com símbolo de moeda e sinal."""
    symbol = {"BRL": "R$", "USD": "US$", "EUR": "€"}.get(currency, currency)
    if value >= 0:
        return f"{symbol} {value:,.2f}"
    return f"−{symbol} {abs(value):,.2f}"

st.set_page_config(page_title="Contas · Inside Cash", layout="wide", page_icon=FAVICON_IMG or "🏦")

is_dark = page_header("Contas Financeiras", "Gerencie suas contas bancárias, caixas e investimentos")
LAYOUT = plotly_layout(is_dark)

_catalog = CatalogService(owner_id=st.session_state.get("effective_owner_id"))

# ── Labels legíveis para os tipos de conta ────────────────────────────────────
_TIPO_LABEL: dict[str, str] = {
    AccountType.CONTA_BANCARIA: "Conta Bancária",
    AccountType.CAIXA:          "Caixa",
    AccountType.COFRE:          "Cofre",
    AccountType.INVESTIMENTOS:  "Investimentos",
    AccountType.PROVISAO:       "Provisão",
    AccountType.OUTRA:          "Outra",
}

# ── Listagem de contas ────────────────────────────────────────────────────────
contas = _catalog.list_accounts_with_entity()

if not contas:
    st.info("Nenhuma conta cadastrada. Crie a primeira conta abaixo.")
else:
    mostrar_inativas = st.checkbox("Mostrar contas inativas", value=False)
    exibir = contas if mostrar_inativas else [c for c in contas if c["is_active"]]

    if not exibir:
        st.info("Nenhuma conta ativa. Marque 'Mostrar contas inativas' para ver todas.")
    else:
        # ── Painel de totais ──────────────────────────────────────────────────
        ativas = [c for c in exibir if c["is_active"]]
        total_brl = sum(c["balance"] for c in ativas if c["currency"] == "BRL")

        col_t1, col_t2, col_t3 = st.columns(3)
        col_t1.metric("Contas ativas", len(ativas))
        col_t2.metric(
            "Saldo total (BRL)",
            _fmt_balance(total_brl),
            delta=None,
        )
        saldo_neg = sum(1 for c in ativas if c["balance"] < 0)
        col_t3.metric("Contas negativas", saldo_neg, delta_color="inverse")

        st.divider()

        for conta in exibir:
            status  = "Ativa" if conta["is_active"] else "Inativa"
            tipo    = _TIPO_LABEL.get(conta["account_type"], conta["account_type"])
            balance = conta["balance"]
            balance_str = _fmt_balance(balance, conta["currency"])
            balance_label = f"🟢 {balance_str}" if balance >= 0 else f"🔴 {balance_str}"

            with st.expander(
                f"{conta['account_name']} — {conta['entity_name']} ({conta['entity_type']})"
                f"  |  {tipo}  |  {balance_label}  |  {status}"
            ):
                col1, col2, col3, col4 = st.columns(4)
                col1.markdown(f"**Tipo:** {tipo}")
                col2.markdown(f"**Moeda:** {conta['currency']}")
                col3.markdown(f"**Entidade:** {conta['entity_name']} ({conta['entity_type']})")
                bal_color = "#4CAF50" if balance >= 0 else "#F44336"
                col4.markdown(
                    f"**Saldo:** <span style='color:{bal_color};font-weight:700'>{balance_str}</span>",
                    unsafe_allow_html=True,
                )

                if conta["description"]:
                    st.caption(conta["description"])

                if conta["is_active"] and not is_reader():
                    if st.button("Desativar conta", key=f"deactivate_{conta['id']}", type="secondary"):
                        _catalog.deactivate_account(conta["id"])
                        st.toast(f"Conta '{conta['account_name']}' desativada.")
                        st.rerun()

st.divider()

# ── Histórico de Saldo por Conta ────────────────────────────────────────────
st.subheader("Histórico de Saldo")

_df_hist = _get_balance_history(st.session_state.get("effective_owner_id"))

if _df_hist.empty:
    st.info("Nenhuma movimentação encontrada. Importe ou registre transações para visualizar o histórico.")
else:
    _all_accounts = sorted(_df_hist["account_name"].unique().tolist())
    _sel = st.multiselect(
        "Contas a visualizar",
        options=_all_accounts,
        default=_all_accounts,
    )
    if _sel:
        _df_filtered = _df_hist[_df_hist["account_name"].isin(_sel)]
        fig_hist = px.line(
            _df_filtered,
            x="date",
            y="balance",
            color="account_name",
            markers=True,
            labels={"date": "Data", "balance": "Saldo (R$)", "account_name": "Conta"},
        )
        fig_hist.add_hline(y=0, line_dash="dot", line_color="rgba(128,128,128,0.5)")
        fig_hist.update_layout(**LAYOUT)
        st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ── Cadastro de nova conta ────────────────────────────────────────────────────
st.subheader("Nova Conta")

entidades = _catalog.list_entities()
if not entidades:
    st.warning("Cadastre pelo menos uma entidade (PF ou PJ) antes de criar uma conta.")
    if st.button("Ir para o Dashboard"):
        st.switch_page("pages/01_dashboard_geral.py")
    st.stop()

opcoes_entidade = {f"{e.name} ({e.entity_type})": e.id for e in entidades}
opcoes_tipo     = {v: k.value for k, v in _TIPO_LABEL.items()}

with st.form("nova_conta", clear_on_submit=True):
    col1, col2 = st.columns(2)
    nome        = col1.text_input("Nome da conta *", placeholder="Ex: Nubank Pessoa Física")
    entidade    = col2.selectbox("Entidade proprietária *", options=list(opcoes_entidade.keys()))
    tipo        = col1.selectbox("Tipo de conta *", options=list(opcoes_tipo.keys()))
    moeda       = col2.selectbox("Moeda", options=["BRL", "USD", "EUR"], index=0)
    descricao   = st.text_input("Descrição (opcional)", placeholder="Ex: Conta corrente principal")

    submitted = st.form_submit_button("Criar conta", type="primary")
    if submitted:
        if not nome.strip():
            st.error("Informe o nome da conta.")
        else:
            try:
                _catalog.create_account(
                    entity_id=opcoes_entidade[entidade],
                    account_name=nome.strip(),
                    account_type=opcoes_tipo[tipo],
                    currency=moeda,
                    description=descricao.strip() or None,
                )
                st.toast(f"Conta '{nome.strip()}' criada com sucesso!", icon="✅")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
