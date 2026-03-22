import pandas as pd
import streamlit as st

from src.analytics.loader import load_transactions_df
from app.ui import FAVICON_IMG,  page_header, TIPO_LABEL
from app.export import generate_excel

st.set_page_config(page_title="Extrato · Inside Money", layout="wide", page_icon=FAVICON_IMG or "📝")


@st.cache_data(ttl=30)
def _get_data(owner_id: int | None) -> pd.DataFrame:
    return load_transactions_df(owner_id=owner_id)


page_header("Extrato", "Tudo que entrou e saiu nas datas selecionadas")

df = _get_data(st.session_state.get("effective_owner_id"))

if df.empty:
    st.info("Nenhuma transação cadastrada ainda. Comece registrando ou importando seu extrato.")
    col_a, col_b, _ = st.columns([2, 2, 4])
    with col_a:
        if st.button("Registrar transação", type="primary"):
            st.switch_page("pages/07_novo_lancamento.py")
    with col_b:
        if st.button("Importar extrato"):
            st.switch_page("pages/05_importacao_dados.py")
    st.stop()

# ── Filtros ────────────────────────────────────────────────────────────────────
st.markdown('<span class="nx-section-label">Filtros</span>', unsafe_allow_html=True)
col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

with col_f2:
    categories = sorted(df["category"].dropna().unique().tolist())
    selected_categories = st.multiselect("Categoria", categories, default=[])

with col_f3:
    entity_types = sorted(df["source_entity_type"].dropna().unique().tolist())
    selected_entity_types = st.multiselect("Origem (PF / PJ)", entity_types, default=[])

with col_f4:
    _all_types = sorted(df["transaction_type"].dropna().unique().tolist())
    _type_label_map = {TIPO_LABEL.get(t, t): t for t in _all_types}
    selected_type_labels = st.multiselect("Tipo", list(_type_label_map.keys()), default=[])
    selected_types = [_type_label_map[lbl] for lbl in selected_type_labels]

# ── Aplicar filtros ────────────────────────────────────────────────────────────
filtered = df.copy()

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start, end = date_range
    filtered = filtered[
        (filtered["date"].dt.date >= start) & (filtered["date"].dt.date <= end)
    ]

if selected_categories:
    filtered = filtered[filtered["category"].isin(selected_categories)]

if selected_entity_types:
    filtered = filtered[filtered["source_entity_type"].isin(selected_entity_types)]

if selected_types:
    filtered = filtered[filtered["transaction_type"].isin(selected_types)]

st.caption(f"{len(filtered)} lançamento(s) encontrado(s)")

# ── Resumo financeiro do período ──────────────────────────────────────────────
_INCOME_TYPES = {"receita", "pro_labore", "dividendos"}
_total_in  = float(filtered[filtered["transaction_type"].isin(_INCOME_TYPES)]["amount"].sum())
_total_out = float(filtered[filtered["transaction_type"] == "despesa"]["amount"].sum())
_saldo     = _total_in - _total_out

_sm1, _sm2, _sm3 = st.columns(3)
_sm1.metric("↑ Entradas", f"R$ {_total_in:,.2f}")
_sm2.metric("↓ Saídas",   f"R$ {_total_out:,.2f}")
_sm3.metric("Saldo",   f"R$ {_saldo:,.2f}")

# ── Tabela completa ────────────────────────────────────────────────────────────
_COL_MAP = {
    "date":               "Data",
    "transaction_type":   "Tipo",
    "description":        "Descrição",
    "category":           "Categoria",
    "source_entity_name": "Entidade",
    "source_entity_type": "Origem",
    "amount":             "Valor (R$)",
    "currency":           "Moeda",
}
cols_present = [c for c in _COL_MAP if c in filtered.columns]
display_df = filtered[cols_present].copy().rename(columns=_COL_MAP)

if "Data" in display_df.columns:
    display_df["Data"] = display_df["Data"].dt.strftime("%d/%m/%Y")
if "Tipo" in display_df.columns:
    display_df["Tipo"] = display_df["Tipo"].map(TIPO_LABEL).fillna(display_df["Tipo"])
if "Valor (R$)" in display_df.columns:
    display_df["Valor (R$)"] = display_df["Valor (R$)"].map("R$ {:,.2f}".format)

st.dataframe(display_df, use_container_width=True, hide_index=True)

excel_bytes = generate_excel(display_df)
st.download_button(
    label="Exportar Excel",
    data=excel_bytes,
    file_name="lancamentos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
