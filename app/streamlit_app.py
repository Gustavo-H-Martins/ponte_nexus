import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.config.database import init_db

st.set_page_config(
    page_title="Ponte Nexus",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

from app.ui import page_header  # noqa: E402

page_header("Ponte Nexus", "Análise financeira integrada entre Pessoa Física e Pessoa Jurídica")

st.markdown(
    """
Use o menu lateral para navegar entre as páginas:

- **Dashboard Geral** — KPIs do período: receitas PJ, receitas PF, despesas e saldo
- **Fluxo PF ↔ PJ** — Transferências, aportes e retiradas entre PF e PJ
- **Distribuição de Renda** — Pró-labore e dividendos por período
- **Investimentos PF na PJ** — Aportes e empréstimos da PF para a PJ
- **Lançamentos** — Lista completa com filtros por período, categoria e entidade
- **Importação de Dados** — Upload de arquivos CSV, XLSX ou JSON
"""
)
