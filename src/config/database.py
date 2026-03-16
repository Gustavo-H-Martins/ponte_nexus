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

    Em desenvolvimento: cria as tabelas via create_all se ainda não existirem.
    Em produção: as tabelas devem ser criadas via `alembic upgrade head`.
    """
    if settings.database_url.startswith("sqlite:///"):
        db_path = Path(settings.database_url.removeprefix("sqlite:///"))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    import src.models.db_models  # noqa: F401 — registra modelos no Base

    if settings.environment == "development":
        # Cria tabelas ausentes sem apagar dados existentes.
        # Em produção, use: alembic upgrade head
        Base.metadata.create_all(bind=engine)
