import streamlit as st

from app.ui import page_header, require_write_access
from src.services.share_service import ShareService

st.set_page_config(page_title="Compartilhamento · Inside Money", layout="wide", page_icon="🔗")

require_write_access()  # readers não podem acessar esta página

page_header("Compartilhamento de Dados", "Convide leitores para visualizar seus dados financeiros")

_owner_id: int = st.session_state["user_id"]
_svc = ShareService()

# ── Leitores atuais ───────────────────────────────────────────────────────────
st.subheader("Leitores com acesso")

readers = _svc.list_readers(_owner_id)

if not readers:
    st.info("Nenhum leitor cadastrado. Convide alguém usando o formulário abaixo.")
else:
    for r in readers:
        col_name, col_email, col_date, col_action = st.columns([2, 3, 2, 1])
        col_name.write(r["username"])
        col_email.write(r["email"])
        col_date.caption(r["created_at"].strftime("%d/%m/%Y") if r["created_at"] else "—")
        if col_action.button("Revogar", key=f"revoke_{r['reader_id']}", type="secondary"):
            _svc.revoke_reader(_owner_id, r["reader_id"])
            st.success(f"Acesso de {r['email']} revogado.")
            st.rerun()

st.divider()

# ── Convidar novo leitor ──────────────────────────────────────────────────────
st.subheader("Convidar leitor")
st.caption(
    "O leitor usará o e-mail e a senha cadastrados aqui para fazer login. "
    "Se o e-mail já estiver cadastrado como reader, ele será reutilizado."
)

with st.form("form_invite_reader", clear_on_submit=True):
    _email    = st.text_input("E-mail do leitor")
    _password = st.text_input("Senha (mínimo 8 caracteres)", type="password")
    _submit   = st.form_submit_button("Convidar", type="primary")

if _submit:
    if not _email or not _password:
        st.error("Preencha e-mail e senha.")
    else:
        try:
            result = _svc.invite_reader(_owner_id, _email, _password)
            if result["already_shared"]:
                st.warning(f"{result['email']} já tem acesso aos seus dados.")
            else:
                st.success(f"Leitor **{result['email']}** convidado com sucesso.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
