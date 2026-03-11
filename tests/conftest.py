import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import src.models.db_models  # noqa: F401 — registra modelos no Base antes de create_all
from src.config.database import Base


@pytest.fixture
def in_memory_session_factory():
    """Sessao SQLite em memoria com schema completo para testes de integracao."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    yield factory
    Base.metadata.drop_all(engine)
