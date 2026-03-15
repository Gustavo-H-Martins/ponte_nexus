import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.config.database import init_db

init_db()

pages = st.navigation(
    {
        "Pessoal": [
            st.Page("pages/08_painel_pessoal.py", title="Meu Bolso", icon="👤"),
            st.Page("pages/10_orcamento.py",      title="Orçamento",  icon="🎯"),
        ],
        "Empresa": [
            st.Page("pages/01_dashboard_geral.py", title="Visão Geral", icon="📊"),
        ],
        "Transações": [
            st.Page("pages/06_lancamentos.py",      title="Extrato",             icon="📋"),
            st.Page("pages/07_novo_lancamento.py",  title="Registrar Transação", icon="✏️"),
            st.Page("pages/05_importacao_dados.py", title="Importar Extrato",    icon="📂"),
        ],
        "Ajuda": [
            st.Page("pages/09_ajuda.py",  title="Como Usar",          icon="❓"),
            st.Page("pages/12_planos.py", title="Planos e Assinatura", icon="⭐"),
        ],
    }
)
pages.run()
