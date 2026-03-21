import base64
import hashlib
import os

from src.config.database import SessionLocal
from src.models.db_models import UserModel
from src.repositories.share_repository import ShareRepository
from src.repositories.user_repository import UserRepository


_PBKDF2_ITERATIONS = 480_000


def _hash_senha(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERATIONS)
    return base64.b64encode(salt + key).decode()


class ShareService:
    """Gerencia o compartilhamento de dados entre proprietários e leitores."""

    def __init__(self, session_factory=SessionLocal) -> None:
        self.session_factory = session_factory

    def invite_reader(self, owner_id: int, reader_email: str, password: str) -> dict:
        """Convida um leitor pelo e-mail.

        Se o e-mail já existir com role=reader, reutiliza a conta.
        Se já existir a permissão, retorna already_shared=True.
        Retorna dict com: user_id, email, username, already_shared.
        Levanta ValueError se o e-mail pertencer a uma conta não-reader.
        """
        if len(password) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")

        with self.session_factory() as session:
            user_repo = UserRepository(session)
            share_repo = ShareRepository(session)

            existing = user_repo.get_by_email(reader_email)
            if existing is not None:
                if existing.role != "reader":
                    raise ValueError("Este e-mail pertence a uma conta que não é reader.")
                reader = existing
                already_existed = True
            else:
                reader = UserModel(
                    email=reader_email.lower().strip(),
                    username=reader_email.split("@")[0],
                    password_hash=_hash_senha(password),
                    role="reader",
                    plan="free",
                )
                session.add(reader)
                session.flush()
                already_existed = False

            already_shared = share_repo.exists(owner_id, reader.id)
            if not already_shared:
                share_repo.create(owner_id, reader.id)

            session.commit()

            # detach para evitar uso fora da sessão
            reader_id   = reader.id
            reader_mail = reader.email
            reader_name = reader.username

        return {
            "user_id":       reader_id,
            "email":         reader_mail,
            "username":      reader_name,
            "already_shared": already_shared,
            "already_existed": already_existed,
        }

    def revoke_reader(self, owner_id: int, reader_id: int) -> None:
        """Remove o acesso de um leitor aos dados do proprietário."""
        with self.session_factory() as session:
            ShareRepository(session).delete(owner_id, reader_id)
            session.commit()

    def list_readers(self, owner_id: int) -> list[dict]:
        """Retorna todos os leitores com acesso aos dados do proprietário."""
        with self.session_factory() as session:
            shares = ShareRepository(session).list_readers_for_owner(owner_id)
            result = []
            for s in shares:
                user = UserRepository(session).get_by_id(s.reader_id)
                if user:
                    result.append({
                        "reader_id":  user.id,
                        "email":      user.email,
                        "username":   user.username,
                        "created_at": s.created_at,
                    })
            return result

    def list_accessible_owners(self, reader_id: int) -> list[dict]:
        """Retorna todos os proprietários que compartilharam dados com o leitor."""
        with self.session_factory() as session:
            shares = ShareRepository(session).list_owners_for_reader(reader_id)
            result = []
            for s in shares:
                user = UserRepository(session).get_by_id(s.owner_id)
                if user:
                    result.append({
                        "owner_id":  user.id,
                        "email":     user.email,
                        "username":  user.username,
                    })
            return result
