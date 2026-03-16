import streamlit as st

from app.ui import page_header
from src.domain.enums import AccountType
from src.services.catalog_service import CatalogService

st.set_page_config(page_title="Contas · Ponte Nexus", layout="wide", page_icon="🏦")

page_header("Contas Financeiras", "Gerencie suas contas bancárias, caixas e investimentos")

_catalog = CatalogService()

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
        for conta in exibir:
            status = "✅ Ativa" if conta["is_active"] else "🔒 Inativa"
            tipo   = _TIPO_LABEL.get(conta["account_type"], conta["account_type"])
            with st.expander(
                f"{conta['account_name']} — {conta['entity_name']} ({conta['entity_type']})  |  {tipo}  |  {status}"
            ):
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"**Tipo:** {tipo}")
                col2.markdown(f"**Moeda:** {conta['currency']}")
                col3.markdown(f"**Entidade:** {conta['entity_name']} ({conta['entity_type']})")

                if conta["description"]:
                    st.caption(conta["description"])

                if conta["is_active"]:
                    if st.button("Desativar conta", key=f"deactivate_{conta['id']}", type="secondary"):
                        _catalog.deactivate_account(conta["id"])
                        st.toast(f"Conta '{conta['account_name']}' desativada.", icon="🔒")
                        st.rerun()

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
