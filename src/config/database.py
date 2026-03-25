from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config.settings import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Inicializa o banco de dados.

    Executa `alembic upgrade head` para garantir que o schema esteja atualizado
    em qualquer ambiente. Em SQLite local, cria o diretório se necessário.
    `alembic upgrade head` é idempotente: não faz nada quando já está no head.
    """
    if settings.database_url.startswith("sqlite:///"):
        db_path = Path(settings.database_url.removeprefix("sqlite:///"))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    import src.models.db_models  # noqa: F401 — registra modelos no Base

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
