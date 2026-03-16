import streamlit as st

from src.services.auth_service import AuthService

st.set_page_config(page_title="Ponte Nexus · Entrar", layout="centered", page_icon="🌉")

_auth = AuthService()

st.title("🌉 Ponte Nexus")
st.caption("Dashboard financeiro PF · PJ")

st.divider()

aba_login, aba_cadastro = st.tabs(["Entrar", "Criar conta"])

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
