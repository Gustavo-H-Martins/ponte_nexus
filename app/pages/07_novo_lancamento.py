from datetime import date
from decimal import Decimal

import streamlit as st

from app.ui import FAVICON_IMG,  TIPO_LABEL, page_header, require_write_access
from src.config.database import SessionLocal, init_db
from src.domain.enums import TransactionType
from src.repositories.account_repository import AccountRepository
from src.repositories.category_repository import CategoryRepository
from src.repositories.entity_repository import EntityRepository
from src.services.catalog_service import CatalogService
from src.services.manual_entry_service import ManualEntryService
from src.validation.schemas import ManualTransactionInput

st.set_page_config(
    page_title="Registrar Transação · Inside Money", layout="wide", page_icon=FAVICON_IMG or "✏️",
    initial_sidebar_state="collapsed",
)

init_db()

page_header(
    "Registrar Transação",
    "Registre uma receita, despesa ou transferência",
)
require_write_access()

# ── Serviços ──────────────────────────────────────────────────────────────────
owner_id: int | None = st.session_state.get("effective_owner_id")
_catalog = CatalogService(owner_id=owner_id)
_entry = ManualEntryService(owner_id=owner_id)

# ── Loaders em cache (TTL curto para refletir cadastros recentes) ─────────────


@st.cache_data(ttl=30)
def _load_entities(owner_id: int | None = None) -> list[dict]:
    with SessionLocal() as session:
        rows = EntityRepository(session, owner_id).list_all()
        return [{"id": r.id, "name": r.name, "entity_type": r.entity_type} for r in rows]


@st.cache_data(ttl=30)
def _load_accounts(owner_id: int | None = None) -> list[dict]:
    with SessionLocal() as session:
        return AccountRepository(session, owner_id).list_with_entity()


@st.cache_data(ttl=30)
def _load_categories(owner_id: int | None = None) -> list[dict]:
    with SessionLocal() as session:
        rows = CategoryRepository(session, owner_id).list_all()
        return [{"id": r.id, "name": r.name, "group": r.category_group} for r in rows]


@st.cache_data(ttl=30)
def _load_companies(owner_id: int | None = None) -> list[dict]:
    return CatalogService(owner_id=owner_id).list_companies()


def _reload_all() -> None:
    _load_entities.clear()
    _load_accounts.clear()
    _load_categories.clear()
    _load_companies.clear()


# ── Controle de versão do formulário (para reset após submit) ─────────────────
if "fv" not in st.session_state:
    st.session_state["fv"] = 0

# ── Constantes de seção de configurações ─────────────────────────────────────
_SEC_ADD = '<span class="nx-section-label">Adicionar</span>'
_SEC_DEL = '<span class="nx-section-label">Remover</span>'

# ── Mapa legível de tipos de transação ───────────────────────────────────────
_TX_LABELS: dict[str, str] = dict(TIPO_LABEL)
_TX_VALUES = list(_TX_LABELS.keys())
_TX_DISPLAY = list(_TX_LABELS.values())

# ── Mapa de tipos de empresa ──────────────────────────────────────────────────
_COMPANY_TYPES = {
    "ltda": "LTDA",
    "sa": "S.A.",
    "mei": "MEI",
    "eireli": "EIRELI",
    "simples": "Simples Nacional",
    "outro": "Outro",
}

# ── Tabs principais ────────────────────────────────────────────────────────────
tab_form, tab_config = st.tabs(["Lançamento de Transação", "Configurações"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FORMULÁRIO DE LANÇAMENTO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_form:
    entities = _load_entities(owner_id)
    all_accounts = _load_accounts(owner_id)
    categories = _load_categories(owner_id)

    fv = st.session_state["fv"]  # versão do formulário para reset de widgets

    # ── Aviso quando catálogo está vazio ──────────────────────────────────────
    if not entities or not all_accounts or not categories:
        missing = []
        if not entities:
            missing.append("entidades")
        if not all_accounts:
            missing.append("contas")
        if not categories:
            missing.append("categorias")
        st.warning(
            f"Cadastre {', '.join(missing)} na aba **Configurações** antes de "
            "registrar um lançamento."
        )

    else:
        col_form, col_preview = st.columns([3, 2], gap="large")

        with col_form:
            st.markdown(
                '<span class="nx-section-label">Dados do Lançamento</span>',
                unsafe_allow_html=True,
            )

            # ── Entidade ──────────────────────────────────────────────────────
            row1a, row1b = st.columns(2)
            with row1a:
                entity_type_sel = st.selectbox(
                    "Tipo de entidade",
                    ["PF", "PJ"],
                    key=f"fv{fv}_entity_type",
                )
            with row1b:
                filtered_entities = [
                    e for e in entities if e["entity_type"] == entity_type_sel
                ]
                if not filtered_entities:
                    st.warning(f"Nenhuma entidade {entity_type_sel} cadastrada.")
                    entity_sel: dict | None = None
                else:
                    entity_names = [e["name"] for e in filtered_entities]
                    entity_name_sel = st.selectbox(
                        "Entidade",
                        entity_names,
                        key=f"fv{fv}_entity",
                    )
                    entity_sel = next(
                        (e for e in filtered_entities if e["name"] == entity_name_sel),
                        None,
                    )

            # ── Contas ────────────────────────────────────────────────────────
            st.markdown(
                '<span class="nx-section-label">Contas</span>',
                unsafe_allow_html=True,
            )
            row2a, row2b = st.columns(2)

            entity_accounts = (
                [a for a in all_accounts if a["entity_id"] == entity_sel["id"]]
                if entity_sel
                else []
            )

            with row2a:
                if not entity_accounts:
                    st.warning("Entidade sem contas cadastradas.")
                    src_account_sel: dict | None = None
                else:
                    src_labels = [a["account_name"] for a in entity_accounts]
                    src_label = st.selectbox(
                        "Conta de origem",
                        src_labels,
                        key=f"fv{fv}_src_account",
                    )
                    src_account_sel = next(
                        (a for a in entity_accounts if a["account_name"] == src_label),
                        None,
                    )

            with row2b:
                dst_labels = [
                    f"{a['entity_name']} — {a['account_name']}" for a in all_accounts
                ]
                dst_label = st.selectbox(
                    "Conta de destino",
                    dst_labels,
                    key=f"fv{fv}_dst_account",
                )
                dst_account_sel = next(
                    (a for a, lbl in zip(all_accounts, dst_labels) if lbl == dst_label),
                    None,
                )

            # ── Detalhes da transação ─────────────────────────────────────────
            st.markdown(
                '<span class="nx-section-label">Detalhes</span>',
                unsafe_allow_html=True,
            )
            row3a, row3b = st.columns(2)
            with row3a:
                tx_date = st.date_input(
                    "Data da transação",
                    value=date.today(),
                    format="DD/MM/YYYY",
                    key=f"fv{fv}_date",
                )
            with row3b:
                tx_type_label = st.selectbox(
                    "Tipo de transação",
                    _TX_DISPLAY,
                    key=f"fv{fv}_tx_type",
                )
                tx_type_value = _TX_VALUES[_TX_DISPLAY.index(tx_type_label)]

            row4a, row4b = st.columns(2)
            with row4a:
                cat_names = [c["name"] for c in categories]
                cat_label = st.selectbox(
                    "Categoria",
                    cat_names,
                    key=f"fv{fv}_category",
                )
                cat_sel = next((c for c in categories if c["name"] == cat_label), None)

            with row4b:
                amount = st.number_input(
                    "Valor (R$)",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    key=f"fv{fv}_amount",
                )

            description = st.text_area(
                "Descrição",
                placeholder="Opcional — descreva o lançamento",
                height=80,
                key=f"fv{fv}_description",
            )

            # ── Botões ────────────────────────────────────────────────────────
            st.markdown("")
            btn_save, btn_cancel, _ = st.columns([2, 1, 3])
            submit = btn_save.button("Salvar lançamento", type="primary")
            cancel = btn_cancel.button("Cancelar")

            if cancel:
                st.session_state["fv"] = fv + 1
                st.rerun()

            if submit:
                # Validação de campos obrigatórios antes de chamar o serviço
                errors: list[str] = []
                if entity_sel is None:
                    errors.append("Selecione uma entidade válida.")
                if src_account_sel is None:
                    errors.append("Selecione uma conta de origem.")
                if dst_account_sel is None:
                    errors.append("Selecione uma conta de destino.")
                if cat_sel is None:
                    errors.append("Selecione uma categoria.")
                if amount <= 0:
                    errors.append("O valor deve ser maior que zero.")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    # Narrowing: validações acima garantem que nenhum destes é None
                    assert entity_sel and src_account_sel and dst_account_sel and cat_sel
                    try:
                        data = ManualTransactionInput(
                            source_entity_id=entity_sel["id"],
                            source_account_id=src_account_sel["id"],
                            destination_account_id=dst_account_sel["id"],
                            transaction_date=tx_date,
                            category_id=cat_sel["id"],
                            description=st.session_state.get(f"fv{fv}_description", ""),
                            amount=Decimal(str(amount)),
                            transaction_type=TransactionType(tx_type_value),
                            currency=src_account_sel.get("currency", "BRL"),
                        )
                        _entry.create_transaction(data)
                        tipo_label = _TX_LABELS.get(tx_type_value, tx_type_value)
                        st.toast(
                            f"{tipo_label} de R$ {amount:,.2f} em {cat_label} registrada!",
                        )
                        _reload_all()
                        st.session_state["fv"] = fv + 1
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Erro ao salvar: {exc}")

        # ── Pré-visualização ──────────────────────────────────────────────────
        with col_preview:
            st.markdown(
                '<span class="nx-section-label">Pré-visualização</span>',
                unsafe_allow_html=True,
            )

            preview_ready = (
                entity_sel is not None
                and src_account_sel is not None
                and dst_account_sel is not None
                and cat_sel is not None
                and amount > 0
            )

            if preview_ready:
                # preview_ready garante que todos os seletores são não-nulos
                assert entity_sel and src_account_sel and dst_account_sel and cat_sel
                fmt_date = (
                    tx_date.strftime("%d/%m/%Y") if isinstance(tx_date, date) else "—"
                )
                color_map = {
                    "receita": "#64FFDA",
                    "despesa": "#FF6B6B",
                    "pro_labore": "#4FC3F7",
                    "dividendos": "#81C784",
                    "aporte_pf_pj": "#FFB74D",
                    "emprestimo_pf_pj": "#CE93D8",
                    "transferencia_pf_pj": "#FFF176",
                    "transferencia_pj_pf": "#80DEEA",
                }
                accent = color_map.get(tx_type_value, "#64FFDA")
                desc_preview = (
                    st.session_state.get(f"fv{fv}_description") or "—"
                )

                st.markdown(
                    f"""
<div style="
    background:#112240;
    border:1px solid {accent}55;
    border-left: 3px solid {accent};
    border-radius:12px;
    padding:1.4rem 1.6rem;
    font-family:'Plus Jakarta Sans',sans-serif;
">
<div style="font-size:0.65rem;font-weight:600;letter-spacing:0.1em;
            text-transform:uppercase;color:{accent};margin-bottom:0.8rem">
    Resumo do Lançamento
</div>
<table style="width:100%;border-collapse:collapse;font-size:0.875rem">
  <tr>
    <td style="color:#8892B0;padding:0.3rem 0;width:45%">Tipo</td>
    <td style="color:#CCD6F6;font-weight:600">
      <span style="background:{accent}22;color:{accent};
                   padding:0.15rem 0.5rem;border-radius:4px;font-size:0.8rem">
        {tx_type_label}
      </span>
    </td>
  </tr>
  <tr>
    <td style="color:#8892B0;padding:0.3rem 0">Data</td>
    <td style="color:#CCD6F6">{fmt_date}</td>
  </tr>
  <tr>
    <td style="color:#8892B0;padding:0.3rem 0">Entidade</td>
    <td style="color:#CCD6F6">{entity_sel['name']} ({entity_type_sel})</td>
  </tr>
  <tr>
    <td style="color:#8892B0;padding:0.3rem 0">Origem</td>
    <td style="color:#CCD6F6">{src_account_sel['account_name']}</td>
  </tr>
  <tr>
    <td style="color:#8892B0;padding:0.3rem 0">Destino</td>
    <td style="color:#CCD6F6">{dst_account_sel['entity_name']} — {dst_account_sel['account_name']}</td>
  </tr>
  <tr>
    <td style="color:#8892B0;padding:0.3rem 0">Categoria</td>
    <td style="color:#CCD6F6">{cat_sel['name']}</td>
  </tr>
  <tr>
    <td style="color:#8892B0;padding:0.3rem 0">Descrição</td>
    <td style="color:#CCD6F6;font-style:{'italic' if desc_preview == '—' else 'normal'}">{desc_preview}</td>
  </tr>
  <tr>
    <td style="color:#8892B0;padding:0.4rem 0;border-top:1px solid #1E3A5F">Valor</td>
    <td style="color:{accent};font-size:1.25rem;font-weight:700;
               border-top:1px solid #1E3A5F">
      R$ {amount:,.2f}
    </td>
  </tr>
</table>
</div>
""",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
<div style="
    background:#112240;
    border:1px dashed #1E3A5F;
    border-radius:12px;
    padding:2rem 1.6rem;
    text-align:center;
    color:#8892B0;
    font-size:0.875rem;
">
    <div style="font-size:2rem;margin-bottom:0.5rem">📋</div>
    Preencha os campos do formulário<br>para ver a pré-visualização aqui.
</div>
""",
                    unsafe_allow_html=True,
                )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_config:
    cfg_cat, cfg_acc, cfg_ent, cfg_emp = st.tabs(
        ["Categorias", "Contas", "Entidades", "Empresas (CNPJ)"]
    )

    # ── Categorias ────────────────────────────────────────────────────────────
    with cfg_cat:
        st.markdown(
            '<span class="nx-section-label">Categorias Cadastradas</span>',
            unsafe_allow_html=True,
        )
        cats = _load_categories(owner_id)
        if cats:
            import pandas as pd

            st.dataframe(
                pd.DataFrame(cats).rename(
                    columns={"id": "ID", "name": "Categoria", "group": "Grupo"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nenhuma categoria cadastrada.")

        col_add_cat, col_del_cat = st.columns(2, gap="large")

        with col_add_cat:
            st.markdown(_SEC_ADD, unsafe_allow_html=True)
            with st.form("form_add_cat", clear_on_submit=True):
                new_cat_name = st.text_input("Nome da categoria", placeholder="ex: Alimentação")
                new_cat_group = st.text_input(
                    "Grupo", value="geral", placeholder="ex: pessoal, empresa"
                )
                if st.form_submit_button("Adicionar categoria", type="primary"):
                    if new_cat_name.strip():
                        try:
                            _catalog.create_category(
                                new_cat_name.strip(), new_cat_group.strip() or "geral"
                            )
                            st.success(f"Categoria **{new_cat_name}** adicionada.")
                            _reload_all()
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Erro: {exc}")
                    else:
                        st.warning("Informe o nome da categoria.")

        with col_del_cat:
            st.markdown(_SEC_DEL, unsafe_allow_html=True)
            if cats:
                cat_del_opts = {c["name"]: c["id"] for c in cats}
                cat_del_name = st.selectbox(
                    "Selecione a categoria", list(cat_del_opts.keys()), key="del_cat_sel"
                )
                if st.button("Remover categoria", key="btn_del_cat"):
                    try:
                        _catalog.delete_category(cat_del_opts[cat_del_name])
                        st.success(f"Categoria **{cat_del_name}** removida.")
                        _reload_all()
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Erro ao remover: {exc}")
            else:
                st.info("Nenhuma categoria para remover.")

    # ── Contas ────────────────────────────────────────────────────────────────
    with cfg_acc:
        st.markdown(
            '<span class="nx-section-label">Contas Cadastradas</span>',
            unsafe_allow_html=True,
        )
        accs = _load_accounts(owner_id)
        if accs:
            import pandas as pd

            st.dataframe(
                pd.DataFrame(accs)[["id", "entity_name", "entity_type", "account_name", "currency"]].rename(
                    columns={
                        "id": "ID",
                        "entity_name": "Entidade",
                        "entity_type": "Tipo",
                        "account_name": "Conta",
                        "currency": "Moeda",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nenhuma conta cadastrada.")

        col_add_acc, col_del_acc = st.columns(2, gap="large")
        entities_for_acc = _load_entities(owner_id)

        with col_add_acc:
            st.markdown(_SEC_ADD, unsafe_allow_html=True)
            with st.form("form_add_acc", clear_on_submit=True):
                if not entities_for_acc:
                    st.warning("Cadastre uma entidade primeiro.")
                    st.form_submit_button("Adicionar conta", disabled=True)
                else:
                    acc_entity_labels = [
                        f"{e['name']} ({e['entity_type']})" for e in entities_for_acc
                    ]
                    acc_entity_sel = st.selectbox("Entidade vinculada", acc_entity_labels)
                    acc_entity = next(
                        (
                            e
                            for e, lbl in zip(entities_for_acc, acc_entity_labels)
                            if lbl == acc_entity_sel
                        ),
                        None,
                    )
                    new_acc_name = st.text_input(
                        "Nome da conta", placeholder="ex: Conta Corrente, Carteira"
                    )
                    new_acc_currency = st.selectbox("Moeda", ["BRL", "USD", "EUR"])
                    if st.form_submit_button("Adicionar conta", type="primary"):
                        if new_acc_name.strip() and acc_entity:
                            try:
                                _catalog.create_account(
                                    acc_entity["id"],
                                    new_acc_name.strip(),
                                    new_acc_currency,
                                )
                                st.success(f"Conta **{new_acc_name}** adicionada.")
                                _reload_all()
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Erro: {exc}")
                        else:
                            st.warning("Informe o nome da conta.")

        with col_del_acc:
            st.markdown(_SEC_DEL, unsafe_allow_html=True)
            if accs:
                acc_del_opts = {
                    f"{a['entity_name']} — {a['account_name']}": a["id"] for a in accs
                }
                acc_del_label = st.selectbox(
                    "Selecione a conta", list(acc_del_opts.keys()), key="del_acc_sel"
                )
                if st.button("Remover conta", key="btn_del_acc"):
                    try:
                        _catalog.delete_account(acc_del_opts[acc_del_label])
                        st.success(f"Conta **{acc_del_label}** removida.")
                        _reload_all()
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Erro ao remover: {exc}")
            else:
                st.info("Nenhuma conta para remover.")

    # ── Entidades ─────────────────────────────────────────────────────────────
    with cfg_ent:
        st.markdown(
            '<span class="nx-section-label">Entidades Cadastradas</span>',
            unsafe_allow_html=True,
        )
        ents = _load_entities(owner_id)
        if ents:
            import pandas as pd

            st.dataframe(
                pd.DataFrame(ents).rename(
                    columns={"id": "ID", "name": "Nome", "entity_type": "Tipo"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nenhuma entidade cadastrada.")

        col_add_ent, col_del_ent = st.columns(2, gap="large")

        with col_add_ent:
            st.markdown(_SEC_ADD, unsafe_allow_html=True)
            with st.form("form_add_ent", clear_on_submit=True):
                new_ent_name = st.text_input("Nome da entidade", placeholder="ex: João Silva")
                new_ent_type = st.selectbox("Tipo", ["PF", "PJ"])
                if st.form_submit_button("Adicionar entidade", type="primary"):
                    if new_ent_name.strip():
                        try:
                            _catalog.create_entity(new_ent_name.strip(), new_ent_type)
                            st.success(f"Entidade **{new_ent_name}** ({new_ent_type}) adicionada.")
                            _reload_all()
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Erro: {exc}")
                    else:
                        st.warning("Informe o nome da entidade.")

        with col_del_ent:
            st.markdown(_SEC_DEL, unsafe_allow_html=True)
            if ents:
                ent_del_opts = {
                    f"{e['name']} ({e['entity_type']})": e["id"] for e in ents
                }
                ent_del_label = st.selectbox(
                    "Selecione a entidade", list(ent_del_opts.keys()), key="del_ent_sel"
                )
                if st.button("Remover entidade", key="btn_del_ent"):
                    try:
                        _catalog.delete_entity(ent_del_opts[ent_del_label])
                        st.success(f"Entidade **{ent_del_label}** removida.")
                        _reload_all()
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Erro ao remover: {exc}")
            else:
                st.info("Nenhuma entidade para remover.")

    # ── Empresas (CNPJ) ───────────────────────────────────────────────────────
    with cfg_emp:
        st.markdown(
            '<span class="nx-section-label">Empresas Cadastradas</span>',
            unsafe_allow_html=True,
        )
        companies = _load_companies(owner_id)
        if companies:
            import pandas as pd

            st.dataframe(
                pd.DataFrame(companies)[["id", "nome_empresa", "cnpj", "company_type"]].rename(
                    columns={
                        "id": "ID",
                        "nome_empresa": "Nome",
                        "cnpj": "CNPJ",
                        "company_type": "Tipo Empresa",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nenhuma empresa cadastrada.")

        col_add_emp, col_del_emp = st.columns(2, gap="large")

        with col_add_emp:
            st.markdown(_SEC_ADD, unsafe_allow_html=True)
            with st.form("form_add_emp", clear_on_submit=True):
                new_emp_name = st.text_input(
                    "Nome da empresa", placeholder="ex: Empresa ABC Ltda"
                )
                new_emp_cnpj = st.text_input(
                    "CNPJ", placeholder="xx.xxx.xxx/xxxx-xx"
                )
                new_emp_type = st.selectbox(
                    "Tipo de empresa", list(_COMPANY_TYPES.values())
                )
                # Mapa reverso para valor interno
                _type_rev = {v: k for k, v in _COMPANY_TYPES.items()}
                if st.form_submit_button("Adicionar empresa", type="primary"):
                    if new_emp_name.strip() and new_emp_cnpj.strip():
                        try:
                            _catalog.create_company(
                                new_emp_name.strip(),
                                new_emp_cnpj.strip(),
                                _type_rev.get(new_emp_type, "outro"),
                            )
                            st.success(f"Empresa **{new_emp_name}** adicionada.")
                            _reload_all()
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Erro: {exc}")
                    else:
                        st.warning("Preencha nome e CNPJ.")

        with col_del_emp:
            st.markdown(_SEC_DEL, unsafe_allow_html=True)
            if companies:
                emp_del_opts = {
                    f"{c['nome_empresa']} ({c['cnpj']})": c["id"] for c in companies
                }
                emp_del_label = st.selectbox(
                    "Selecione a empresa", list(emp_del_opts.keys()), key="del_emp_sel"
                )
                if st.button("Remover empresa", key="btn_del_emp"):
                    try:
                        _catalog.delete_company(emp_del_opts[emp_del_label])
                        st.success(f"Empresa **{emp_del_label}** removida.")
                        _reload_all()
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Erro ao remover: {exc}")
            else:
                st.info("Nenhuma empresa para remover.")
