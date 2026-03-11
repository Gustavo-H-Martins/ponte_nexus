from pathlib import Path

import streamlit as st

from src.fin_dashboard.core.database import init_db


st.set_page_config(page_title="Painel Financeiro", layout="wide")
init_db()

st.title("Painel de Analise Financeira")
st.caption("Empresarios e autonomos com multiplas fontes de renda")

st.markdown(
    """
### Estrutura inicial pronta
- Importe suas transacoes na pagina **Importacao**
- Explore indicadores nas paginas de analise

Diretorios de dados:
- `data/raw` para arquivos de entrada
- `data/processed` para dados transformados
"""
)

st.info(f"Base SQLite em: {Path('data/finance.db').resolve()}")
