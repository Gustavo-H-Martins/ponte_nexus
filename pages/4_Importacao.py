from pathlib import Path

import streamlit as st

from src.fin_dashboard.config import RAW_DIR
from src.fin_dashboard.services.ingestion_service import import_transactions

st.title("Importacao")
uploaded = st.file_uploader("Envie um CSV padrao", type=["csv"])

if uploaded is not None:
    target = Path(RAW_DIR) / uploaded.name
    target.write_bytes(uploaded.read())
    imported = import_transactions(target)
    st.success(f"{imported} transacoes importadas com sucesso.")

st.caption("Colunas esperadas: nome_entidade, data, descricao, categoria, tipo_transacao, valor, conta_origem")
