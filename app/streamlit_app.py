import sys
from pathlib import Path

# Garante que a raiz do repositório esteja em sys.path independente de como
# o Streamlit Cloud configura o ambiente (ele adiciona app/ mas não a raiz).
_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st
from PIL import Image as _PIL_Image

from app.ui import is_reader, FAVICON_IMG, LOGO_PATH
from src.config.database import init_db
from src.services.share_service import ShareService

init_db()

# ── Guard de autenticação ─────────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.navigation([st.Page("pages/00_login.py", title="Entrar", icon="🔑")]).run()
    st.stop()

# ── Logo fixo acima do menu de navegação (st.logo prega no topo da sidebar) ──
_is_dark_now = st.session_state.get("dark_mode", True)
_logo_light = str(LOGO_PATH / "logo_imoney_light.png")
_logo_dark  = str(LOGO_PATH / "logo_imoney_pill.png")
st.logo(
    image=_logo_dark if _is_dark_now else _logo_light,
    size="large",
)
# Sobrepõe o tamanho máximo imposto pelo Streamlit ao st.logo()
st.markdown(
    """
    <style>
    [data-testid="stLogoImage"] {
        width: 180px !important;
        max-width: 180px !important;
        height: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar: info do usuário + logout ─────────────────────────────────────────
with st.sidebar:
    st.caption(f"👤 **{st.session_state.get('username', '')}**")
    st.caption(st.session_state.get("user_email", ""))
    if st.button("Sair", use_container_width=True):
        for key in ["user_id", "user_email", "username", "user_role", "user_plan", "effective_owner_id"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.divider()

    # ── Para readers: selectbox de proprietário compartilhado ────────────────
    if is_reader():
        _owners = ShareService().list_accessible_owners(st.session_state["user_id"])
        if not _owners:
            st.warning("Nenhum proprietário compartilhou dados com você ainda.")
            st.stop()
        _owner_labels = {o["owner_id"]: f"{o['username']} ({o['email']})" for o in _owners}
        _selected = st.selectbox(
            "Visualizando dados de:",
            options=list(_owner_labels.keys()),
            format_func=lambda oid: _owner_labels[oid],
            key="_sidebar_owner_select",
        )
        st.session_state["effective_owner_id"] = _selected
    else:
        st.session_state["effective_owner_id"] = st.session_state["user_id"]

# ── Navegação ─────────────────────────────────────────────────────────────────
_nav: dict = {
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

if not is_reader():
    _nav["Ajuda"].append(
        st.Page("pages/15_compartilhamento.py", title="Compartilhamento", icon="🔗")
    )

if st.session_state.get("user_role") == "admin":
    _nav["Ajuda"].append(
        st.Page("pages/16_admin.py", title="Painel Admin", icon="🛡️")
    )

st.navigation(_nav).run()
