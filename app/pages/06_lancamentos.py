import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from src.analytics.loader import load_transactions_df


@st.cache_data(ttl=30)
def _get_data() -> pd.DataFrame:
    return load_transactions_df()


st.title("Lançamentos")
st.caption("Lista completa de lançamentos com filtros")

df = _get_data()

if df.empty:
    st.info("Nenhum lançamento encontrado. Importe dados na página Importação de Dados.")
    st.stop()

# --- Filtros ---
st.subheader("Filtros")
col_f1, col_f2, col_f3 = st.columns(3)

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

# --- Aplicar filtros ---
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

st.caption(f"{len(filtered)} lançamento(s) encontrado(s)")

# --- Tabela completa ---
_COL_MAP = {
    "date": "Data",
    "transaction_type": "Tipo",
    "description": "Descrição",
    "category": "Categoria",
    "source_entity_name": "Entidade",
    "source_entity_type": "Origem",
    "amount": "Valor (R$)",
    "currency": "Moeda",
}
cols_present = [c for c in _COL_MAP if c in filtered.columns]
display_df = filtered[cols_present].copy().rename(columns=_COL_MAP)

if "Data" in display_df.columns:
    display_df["Data"] = display_df["Data"].dt.strftime("%d/%m/%Y")
if "Valor (R$)" in display_df.columns:
    display_df["Valor (R$)"] = display_df["Valor (R$)"].map("R$ {:,.2f}".format)

st.dataframe(display_df, use_container_width=True, hide_index=True)
