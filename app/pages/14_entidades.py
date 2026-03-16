import streamlit as st

from app.ui import page_header
from src.domain.enums import EntityType
from src.services.catalog_service import CatalogService

st.set_page_config(page_title="Entidades · Ponte Nexus", layout="wide", page_icon="🏢")

page_header("Entidades", "Gerencie pessoas físicas (PF) e jurídicas (PJ) cadastradas no sistema")

_catalog = CatalogService()

# ── Abas por tipo de entidade ─────────────────────────────────────────────────
aba_pj, aba_pf = st.tabs(["🏢 Pessoas Jurídicas (PJ)", "👤 Pessoas Físicas (PF)"])

with aba_pj:
    entidades_pj = _catalog.list_entities(entity_type=EntityType.PJ.value)

    if not entidades_pj:
        st.info("Nenhuma PJ cadastrada.")
    else:
        for ent in entidades_pj:
            contas_vinculadas = _catalog.list_accounts(entity_id=ent.id)
            n_contas = len(contas_vinculadas)

            with st.expander(f"**{ent.name}**  |  ID #{ent.id}  |  {n_contas} conta(s)"):
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**Tipo:** Pessoa Jurídica  |  **ID:** {ent.id}")

                if n_contas > 0:
                    col2.button(
                        "Excluir",
                        key=f"del_pj_{ent.id}",
                        type="secondary",
                        disabled=True,
                        help=f"Esta entidade possui {n_contas} conta(s) vinculada(s). Desative ou exclua as contas antes de remover a entidade.",
                    )
                else:
                    if col2.button("Excluir", key=f"del_pj_{ent.id}", type="secondary"):
                        _catalog.delete_entity(ent.id)
                        st.toast(f"Entidade '{ent.name}' removida.", icon="🗑️")
                        st.rerun()

with aba_pf:
    entidades_pf = _catalog.list_entities(entity_type=EntityType.PF.value)

    if not entidades_pf:
        st.info("Nenhuma PF cadastrada.")
    else:
        for ent in entidades_pf:
            contas_vinculadas = _catalog.list_accounts(entity_id=ent.id)
            n_contas = len(contas_vinculadas)

            with st.expander(f"**{ent.name}**  |  ID #{ent.id}  |  {n_contas} conta(s)"):
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**Tipo:** Pessoa Física  |  **ID:** {ent.id}")

                if n_contas > 0:
                    col2.button(
                        "Excluir",
                        key=f"del_pf_{ent.id}",
                        type="secondary",
                        disabled=True,
                        help=f"Esta entidade possui {n_contas} conta(s) vinculada(s). Desative ou exclua as contas antes de remover a entidade.",
                    )
                else:
                    if col2.button("Excluir", key=f"del_pf_{ent.id}", type="secondary"):
                        _catalog.delete_entity(ent.id)
                        st.toast(f"Entidade '{ent.name}' removida.", icon="🗑️")
                        st.rerun()

st.divider()

# ── Cadastro de nova entidade ─────────────────────────────────────────────────
st.subheader("Nova Entidade")

with st.form("nova_entidade", clear_on_submit=True):
    col1, col2 = st.columns(2)
    nome = col1.text_input("Nome *", placeholder="Ex: João Silva ou Acme Ltda")
    tipo = col2.selectbox(
        "Tipo *",
        options=["Pessoa Jurídica (PJ)", "Pessoa Física (PF)"],
        index=0,
    )

    submitted = st.form_submit_button("Cadastrar entidade", type="primary")
    if submitted:
        if not nome.strip():
            st.error("Informe o nome da entidade.")
        else:
            entity_type = EntityType.PJ.value if "PJ" in tipo else EntityType.PF.value
            try:
                _catalog.create_entity(nome.strip(), entity_type)
                st.toast(f"Entidade '{nome.strip()}' ({entity_type}) cadastrada!", icon="✅")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
