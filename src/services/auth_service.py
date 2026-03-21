import re

try:
    import bcrypt
except ModuleNotFoundError:  # pragma: no cover - depende do ambiente de runtime
    bcrypt = None  # type: ignore[assignment]

from src.config.database import SessionLocal
from src.models.db_models import UserModel
from src.repositories.user_repository import UserRepository

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validar_email(email: str) -> None:
    if not _EMAIL_RE.match(email):
        raise ValueError("Formato de e-mail inválido.")


def _hash_senha(password: str) -> str:
    if bcrypt is None:
        raise RuntimeError("Dependencia ausente: instale 'bcrypt' para habilitar autenticacao.")
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verificar_senha(password: str, password_hash: str) -> bool:
    if bcrypt is None:
        raise RuntimeError("Dependencia ausente: instale 'bcrypt' para habilitar autenticacao.")
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def _detach_user(u: UserModel) -> UserModel:
    u.id; u.email; u.username; u.password_hash; u.role; u.plan; u.is_active  # noqa: E702
    return u


class AuthService:
    """Registro, autenticação e consulta de usuários.

    Senhas armazenadas exclusivamente como hash bcrypt — nunca em texto plano.
    """

    def __init__(self, session_factory=SessionLocal) -> None:
        self.session_factory = session_factory

    def register(
        self,
        email: str,
        username: str,
        password: str,
        role: str = "user",
        plan: str = "free",
    ) -> UserModel:
        """Cria um novo usuário. Levanta ValueError se e-mail já existir ou dados inválidos."""
        _validar_email(email)
        if len(password) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if not username.strip():
            raise ValueError("O nome de usuário não pode ser vazio.")

        with self.session_factory() as session:
            repo = UserRepository(session)
            if repo.get_by_email(email):
                raise ValueError("E-mail já cadastrado.")
            user = repo.create(
                email=email,
                username=username,
                password_hash=_hash_senha(password),
                role=role,
                plan=plan,
            )
            session.commit()
            return _detach_user(user)

    def login(self, email: str, password: str) -> UserModel | None:
        """Autentica usuário por e-mail e senha. Retorna None se credenciais inválidas."""
        with self.session_factory() as session:
            user = UserRepository(session).get_by_email(email)
            if user is None or not user.is_active:
                return None
            if not _verificar_senha(password, user.password_hash):
                return None
            return _detach_user(user)

    def get_user_by_id(self, user_id: int) -> UserModel | None:
        """Retorna o usuário pelo ID ou None se não encontrado."""
        with self.session_factory() as session:
            user = UserRepository(session).get_by_id(user_id)
            if user is None:
                return None
            return _detach_user(user)
