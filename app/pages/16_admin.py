import streamlit as st

from app.ui import FAVICON_IMG,  page_header
from src.config.database import SessionLocal
from src.repositories.user_repository import UserRepository

st.set_page_config(page_title="Admin · Inside Cash", layout="wide", page_icon=FAVICON_IMG or "🛡️")

# ── Guard: somente admins ─────────────────────────────────────────────────────
if st.session_state.get("user_role") != "admin":
    st.error("Acesso restrito a administradores.")
    st.stop()

page_header("Painel Administrativo", "Gerencie usuários, planos e permissões")

_PLAN_OPTS  = ["free", "pro", "business"]
_ROLE_OPTS  = ["user", "admin", "reader"]
_PLAN_LABEL = {"free": "Gratuito", "pro": "Pro", "business": "Business"}
_ROLE_LABEL = {"user": "Usuário", "admin": "Admin", "reader": "Leitor"}
_PLAN_COLOR = {"free": "#8892B0", "pro": "#64FFDA", "business": "#FFD600"}
_ROLE_COLOR = {"user": "#8892B0", "admin": "#FF6B6B", "reader": "#BB86FC"}


@st.cache_data(ttl=5)
def _load_users() -> list[dict]:
    with SessionLocal() as session:
        users = UserRepository(session).list_all()
        return [
            {
                "id":         u.id,
                "email":      u.email,
                "username":   u.username,
                "role":       u.role,
                "plan":       u.plan,
                "is_active":  u.is_active,
                "created_at": u.created_at,
            }
            for u in users
        ]


def _badge(text: str, color: str) -> str:
    return (
        f'<span style="background:{color}22;color:{color};border-radius:5px;'
        f'padding:2px 8px;font-size:0.75rem;font-weight:600;">{text}</span>'
    )


# ── Filtros ───────────────────────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
_search   = col_f1.text_input("Buscar por e-mail ou nome", placeholder="@")
_flt_plan = col_f2.selectbox("Filtrar por plano", ["Todos"] + _PLAN_OPTS, format_func=lambda v: "Todos" if v == "Todos" else _PLAN_LABEL[v])
_flt_role = col_f3.selectbox("Filtrar por role",  ["Todos"] + _ROLE_OPTS, format_func=lambda v: "Todos" if v == "Todos" else _ROLE_LABEL[v])

users = _load_users()

if _search:
    q = _search.lower()
    users = [u for u in users if q in u["email"] or q in u["username"].lower()]
if _flt_plan != "Todos":
    users = [u for u in users if u["plan"] == _flt_plan]
if _flt_role != "Todos":
    users = [u for u in users if u["role"] == _flt_role]

st.caption(f"{len(users)} usuário(s) encontrado(s)")
st.divider()

# ── Tabela de usuários ────────────────────────────────────────────────────────
if not users:
    st.info("Nenhum usuário encontrado com os filtros aplicados.")
else:
    for u in users:
        plan_badge = _badge(_PLAN_LABEL[u["plan"]], _PLAN_COLOR.get(u["plan"], "#8892B0"))
        role_badge = _badge(_ROLE_LABEL[u["role"]], _ROLE_COLOR.get(u["role"], "#8892B0"))
        status_icon = "🟢" if u["is_active"] else "🔴"

        with st.expander(
            f"{status_icon} **{u['username']}** — {u['email']}",
            expanded=False,
        ):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**ID:** {u['id']}")
            c2.markdown(f"**Criado em:** {u['created_at'].strftime('%d/%m/%Y') if u['created_at'] else '—'}")
            c3.markdown(f"**Status:** {'Ativo' if u['is_active'] else 'Inativo'}")

            st.markdown(
                f"**Plano atual:** {plan_badge} &nbsp;&nbsp; **Role atual:** {role_badge}",
                unsafe_allow_html=True,
            )
            st.markdown("")

            # Impede que admin altere a própria role acidentalmente
            _is_self = u["id"] == st.session_state.get("user_id")

            col_plan, col_role, col_active, col_save = st.columns([2, 2, 2, 1])

            new_plan = col_plan.selectbox(
                "Plano",
                options=_PLAN_OPTS,
                index=_PLAN_OPTS.index(u["plan"]),
                format_func=lambda v: _PLAN_LABEL[v],
                key=f"plan_{u['id']}",
            )
            new_role = col_role.selectbox(
                "Role",
                options=_ROLE_OPTS,
                index=_ROLE_OPTS.index(u["role"]),
                format_func=lambda v: _ROLE_LABEL[v],
                key=f"role_{u['id']}",
                disabled=_is_self,
                help="Não é possível alterar sua própria role." if _is_self else None,
            )
            toggle_label = "Desativar" if u["is_active"] else "Reativar"
            col_active.markdown("<br>", unsafe_allow_html=True)
            do_toggle = col_active.button(
                toggle_label,
                key=f"toggle_{u['id']}",
                disabled=_is_self,
                help="Não é possível desativar sua própria conta." if _is_self else None,
            )
            col_save.markdown("<br>", unsafe_allow_html=True)
            do_save = col_save.button("Salvar", key=f"save_{u['id']}", type="primary")

            if do_save:
                with SessionLocal() as session:
                    repo = UserRepository(session)
                    if new_plan != u["plan"]:
                        repo.update_plan(u["id"], new_plan)
                    if new_role != u["role"] and not _is_self:
                        repo.update_role(u["id"], new_role)
                    session.commit()
                _load_users.clear()
                st.toast(f"Usuário '{u['email']}' atualizado.")
                st.rerun()

            if do_toggle:
                with SessionLocal() as session:
                    repo = UserRepository(session)
                    repo.toggle_active(u["id"])
                    session.commit()
                _load_users.clear()
                st.toast(f"Conta '{u['email']}' {'desativada' if u['is_active'] else 'reativada'}.")
                st.rerun()
