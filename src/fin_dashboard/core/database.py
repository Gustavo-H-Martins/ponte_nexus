from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.fin_dashboard.config import DB_PATH, ensure_dirs


class Base(DeclarativeBase):
    pass


ensure_dirs()
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    from src.fin_dashboard.models.entities import Transaction  # noqa: F401

    Base.metadata.create_all(bind=engine)
