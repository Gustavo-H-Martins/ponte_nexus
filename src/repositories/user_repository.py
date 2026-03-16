from sqlalchemy import select

from src.models.db_models import UserModel
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        return self.session.scalar(stmt)

    def get_by_id(self, user_id: int) -> UserModel | None:
        return self.session.get(UserModel, user_id)

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
