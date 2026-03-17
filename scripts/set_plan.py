"""Script para gerenciar planos e roles de usuários via linha de comando.

Uso:
    pipenv run python -m scripts.set_plan <email> <plano>
    pipenv run python -m scripts.set_plan <email> --role <role>
    pipenv run python -m scripts.set_plan --list

Exemplos:
    pipenv run python -m scripts.set_plan joao@email.com pro
    pipenv run python -m scripts.set_plan joao@email.com business
    pipenv run python -m scripts.set_plan joao@email.com free
    pipenv run python -m scripts.set_plan joao@email.com --role admin
    pipenv run python -m scripts.set_plan --list
"""

import argparse
import sys

from src.config.database import SessionLocal, init_db
from src.repositories.user_repository import UserRepository

_PLAN_LABEL = {"free": "Gratuito", "pro": "Pro", "business": "Business"}
_ROLE_LABEL = {"user": "Usuário", "admin": "Admin", "reader": "Leitor"}


def _fmt_user(u) -> str:
    plan = _PLAN_LABEL.get(u.plan, u.plan)
    role = _ROLE_LABEL.get(u.role, u.role)
    status = "ativo" if u.is_active else "INATIVO"
    return f"  [{u.id:>4}] {u.email:<40} plano={plan:<10} role={role:<8} {status}"


def cmd_list() -> None:
    init_db()
    with SessionLocal() as session:
        users = UserRepository(session).list_all()
    if not users:
        print("Nenhum usuário cadastrado.")
        return
    print(f"\n{'ID':>6}  {'E-mail':<40} {'Plano':<10} {'Role':<8} Status")
    print("-" * 80)
    for u in users:
        print(_fmt_user(u))
    print(f"\nTotal: {len(users)} usuário(s)")


def cmd_set_plan(email: str, plan: str) -> None:
    init_db()
    with SessionLocal() as session:
        repo = UserRepository(session)
        user = repo.get_by_email(email)
        if user is None:
            print(f"ERRO: E-mail '{email}' não encontrado.", file=sys.stderr)
            sys.exit(1)
        old_plan = user.plan
        repo.update_plan(user.id, plan)
        session.commit()
        print(f"✔ Plano de '{user.email}' atualizado: {_PLAN_LABEL.get(old_plan, old_plan)} → {_PLAN_LABEL.get(plan, plan)}")


def cmd_set_role(email: str, role: str) -> None:
    init_db()
    with SessionLocal() as session:
        repo = UserRepository(session)
        user = repo.get_by_email(email)
        if user is None:
            print(f"ERRO: E-mail '{email}' não encontrado.", file=sys.stderr)
            sys.exit(1)
        old_role = user.role
        repo.update_role(user.id, role)
        session.commit()
        print(f"✔ Role de '{user.email}' atualizada: {_ROLE_LABEL.get(old_role, old_role)} → {_ROLE_LABEL.get(role, role)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gerencia planos e roles de usuários do Ponte Nexus.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("email", nargs="?", help="E-mail do usuário")
    parser.add_argument("plan", nargs="?", choices=["free", "pro", "business"], help="Plano a aplicar")
    parser.add_argument("--role", choices=["user", "admin", "reader"], help="Role a aplicar")
    parser.add_argument("--list", action="store_true", help="Listar todos os usuários")

    args = parser.parse_args()

    if args.list:
        cmd_list()
        return

    if not args.email:
        parser.print_help()
        sys.exit(1)

    if args.role:
        cmd_set_role(args.email, args.role)
    elif args.plan:
        cmd_set_plan(args.email, args.plan)
    else:
        parser.error("Informe um plano (free/pro/business) ou --role (user/admin/reader).")


if __name__ == "__main__":
    main()
