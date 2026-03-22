import sys
from pathlib import Path
_REPO_ROOT = Path(__file__).parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st
from PIL import Image as _PIL_Image

from src.services.auth_service import AuthService
from app.ui import FAVICON_IMG, LOGO_PATH, render_footer

st.set_page_config(
    page_title="Inside Cash · Entrar",
    layout="centered",
    page_icon=FAVICON_IMG or "💰",
)

_auth = AuthService()

# Logo fixo no topo da sidebar via st.logo
st.logo(str(LOGO_PATH / "logo_imoney_light.png"), icon_image=FAVICON_IMG, size="large")
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

# Logo central na área de conteúdo da página de login
_logo_file = LOGO_PATH / "logo_imoney_light.png"
if _logo_file.exists():
    st.image(str(_logo_file), width=240)
else:
    st.title("💰 Inside Cash")
st.caption("Dashboard financeiro PF · PJ")

render_footer(is_dark=False)

st.divider()

aba_login, aba_cadastro, aba_reset = st.tabs(["Entrar", "Criar conta", "Redefinir senha"])

with aba_login:
    with st.form("form_login"):
        email    = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Preencha e-mail e senha.")
        else:
            user = _auth.login(email, password)
            if user is None:
                st.error("Credenciais inválidas ou conta inativa.")
            else:
                st.session_state["user_id"]   = user.id
                st.session_state["user_email"] = user.email
                st.session_state["username"]   = user.username
                st.session_state["user_role"]  = user.role
                st.session_state["user_plan"]  = user.plan
                st.rerun()

with aba_cadastro:
    with st.form("form_cadastro"):
        nome     = st.text_input("Nome")
        email_c  = st.text_input("E-mail", key="cad_email")
        senha1   = st.text_input("Senha (mín. 8 caracteres)", type="password", key="cad_senha1")
        senha2   = st.text_input("Confirmar senha", type="password", key="cad_senha2")
        submitted_c = st.form_submit_button("Criar conta", type="primary", use_container_width=True)

    if submitted_c:
        if not nome or not email_c or not senha1 or not senha2:
            st.error("Preencha todos os campos.")
        elif senha1 != senha2:
            st.error("As senhas não coincidem.")
        else:
            try:
                user = _auth.register(email=email_c, username=nome, password=senha1)
                st.session_state["user_id"]   = user.id
                st.session_state["user_email"] = user.email
                st.session_state["username"]   = user.username
                st.session_state["user_role"]  = user.role
                st.session_state["user_plan"]  = user.plan
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

with aba_reset:
    st.caption("Use esta opção se não consegue entrar com sua senha atual.")
    with st.form("form_reset"):
        email_r  = st.text_input("E-mail da conta", key="reset_email")
        senha_r1 = st.text_input("Nova senha (mín. 8 caracteres)", type="password", key="reset_senha1")
        senha_r2 = st.text_input("Confirmar nova senha", type="password", key="reset_senha2")
        submitted_r = st.form_submit_button("Redefinir senha", type="primary", use_container_width=True)

    if submitted_r:
        if not email_r or not senha_r1 or not senha_r2:
            st.error("Preencha todos os campos.")
        elif senha_r1 != senha_r2:
            st.error("As senhas não coincidem.")
        else:
            try:
                user = _auth.update_password(email=email_r, new_password=senha_r1)
                if user is None:
                    st.error("E-mail não encontrado ou conta inativa.")
                else:
                    st.session_state["user_id"]   = user.id
                    st.session_state["user_email"] = user.email
                    st.session_state["username"]   = user.username
                    st.session_state["user_role"]  = user.role
                    st.session_state["user_plan"]  = user.plan
                    st.rerun()
            except ValueError as exc:
                st.error(str(exc))
