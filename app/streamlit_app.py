import streamlit as st
from src.config.database import init_db
init_db()

# ── Guard de autenticação ─────────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.navigation([st.Page("pages/00_login.py", title="Entrar", icon="🔑")]).run()
    st.stop()

# ── Sidebar: info do usuário + logout ─────────────────────────────────────────
with st.sidebar:
    st.caption(f"👤 **{st.session_state.get('username', '')}**")
    st.caption(st.session_state.get("user_email", ""))
    if st.button("Sair", use_container_width=True):
        for key in ["user_id", "user_email", "username", "user_role", "user_plan"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.divider()

pages = st.navigation(
    {
        "Pessoal": [
            st.Page("pages/08_painel_pessoal.py", title="Meu Bolso", icon="👤"),
            st.Page("pages/10_orcamento.py",      title="Orçamento",  icon="🎯"),
        ],
        "Empresa": [
            st.Page("pages/01_dashboard_geral.py", title="Visão Geral",  icon="📊"),
            st.Page("pages/13_contas.py",          title="Contas",        icon="🏦"),
            st.Page("pages/14_entidades.py",       title="Entidades",     icon="🏢"),
        ],
        "Transações": [
            st.Page("pages/06_lancamentos.py",      title="Extrato",             icon="📝"),
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
