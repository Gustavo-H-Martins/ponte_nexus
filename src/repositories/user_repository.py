from sqlalchemy import select

from src.models.db_models import UserModel
from src.repositories.base import BaseRepository

_VALID_PLANS = {"free", "pro", "business"}
_VALID_ROLES = {"user", "admin", "reader"}


class UserRepository(BaseRepository):
    def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        return self.session.scalar(stmt)

    def get_by_id(self, user_id: int) -> UserModel | None:
        return self.session.get(UserModel, user_id)

    def list_all(self) -> list[UserModel]:
        stmt = select(UserModel).order_by(UserModel.created_at.desc())
        return list(self.session.scalars(stmt))

    def update_plan(self, user_id: int, plan: str) -> UserModel:
        if plan not in _VALID_PLANS:
            raise ValueError(f"Plano inválido: {plan!r}. Use: {_VALID_PLANS}")
        user = self.get_by_id(user_id)
        if user is None:
            raise ValueError(f"Usuário {user_id} não encontrado.")
        user.plan = plan
        self.session.flush()
        return user

    def update_role(self, user_id: int, role: str) -> UserModel:
        if role not in _VALID_ROLES:
            raise ValueError(f"Role inválida: {role!r}. Use: {_VALID_ROLES}")
        user = self.get_by_id(user_id)
        if user is None:
            raise ValueError(f"Usuário {user_id} não encontrado.")
        user.role = role
        self.session.flush()
        return user

    def toggle_active(self, user_id: int) -> UserModel:
        user = self.get_by_id(user_id)
        if user is None:
            raise ValueError(f"Usuário {user_id} não encontrado.")
        user.is_active = not user.is_active
        self.session.flush()
        return user

    def create(
        self,
        email: str,
        username: str,
        password_hash: str,
        role: str = "user",
        plan: str = "free",
    ) -> UserModel:
        user = UserModel(
            email=email.lower().strip(),
            username=username.strip(),
            password_hash=password_hash,
            role=role,
            plan=plan,
        )
        self.session.add(user)
        self.session.flush()
        return user
