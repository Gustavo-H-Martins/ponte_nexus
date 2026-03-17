"""Testes unitários do ManualEntryService usando banco SQLite em memória."""
from datetime import date
from decimal import Decimal

import pytest

from src.domain.enums import TransactionType
from src.services.catalog_service import CatalogService
from src.services.manual_entry_service import ManualEntryService
from src.validation.schemas import ManualTransactionInput


@pytest.fixture
def seed(in_memory_session_factory):
    """Cria entidades, contas e categorias mínimas e retorna um dict com seus IDs."""
    catalog = CatalogService(session_factory=in_memory_session_factory)

    pf = catalog.create_entity("João", "PF")
    pj = catalog.create_entity("Empresa X", "PJ")
    acc_pf = catalog.create_account(pf.id, "Conta PF", "conta_bancaria", "BRL")
    acc_pj = catalog.create_account(pj.id, "Conta PJ", "conta_bancaria", "BRL")
    cat    = catalog.create_category("Receita", "geral")

    return {
        "session_factory": in_memory_session_factory,
        "pf_id": pf.id,
        "pj_id": pj.id,
        "acc_pf_id": acc_pf.id,
        "acc_pj_id": acc_pj.id,
        "cat_id": cat.id,
    }


def _input(seed: dict, **overrides) -> ManualTransactionInput:
    """Constrói um ManualTransactionInput válido com possibilidade de sobrescrever campos."""
    defaults = dict(
        source_entity_id=seed["pf_id"],
        source_account_id=seed["acc_pf_id"],
        destination_account_id=seed["acc_pj_id"],
        transaction_date=date(2026, 3, 1),
        category_id=seed["cat_id"],
        description="Transferência de teste",
        amount=Decimal("500.00"),
        transaction_type=TransactionType.TRANSFERENCIA_PF_PJ,
        currency="BRL",
    )
    defaults.update(overrides)
    return ManualTransactionInput(**defaults)


# ── Caminho feliz ──────────────────────────────────────────────────────────────

def test_create_transaction_persiste(seed):
    svc = ManualEntryService(session_factory=seed["session_factory"])
    svc.create_transaction(_input(seed))

    # Confirma via catalog (saldo da conta de destino ≠ 0 após crédito)
    catalog = CatalogService(session_factory=seed["session_factory"])
    contas = catalog.list_accounts_with_entity()
    dest = next(c for c in contas if c["id"] == seed["acc_pj_id"])
    assert dest["balance"] == Decimal("500.00")


def test_create_transaction_debita_conta_origem(seed):
    svc = ManualEntryService(session_factory=seed["session_factory"])
    svc.create_transaction(_input(seed, amount=Decimal("200.00")))

    catalog = CatalogService(session_factory=seed["session_factory"])
    contas = catalog.list_accounts_with_entity()
    origem = next(c for c in contas if c["id"] == seed["acc_pf_id"])
    assert origem["balance"] == Decimal("-200.00")


def test_create_transaction_gera_external_id_unico(seed):
    svc = ManualEntryService(session_factory=seed["session_factory"])
    svc.create_transaction(_input(seed))
    svc.create_transaction(_input(seed))  # second call must not raise (unique UUID)

    catalog = CatalogService(session_factory=seed["session_factory"])
    contas = catalog.list_accounts_with_entity()
    dest = next(c for c in contas if c["id"] == seed["acc_pj_id"])
    assert dest["balance"] == Decimal("1000.00")


def test_create_transaction_conta_destino_inexistente_levanta_error(seed):
    svc = ManualEntryService(session_factory=seed["session_factory"])
    with pytest.raises(ValueError, match="não encontrada"):
        svc.create_transaction(_input(seed, destination_account_id=9999))


# ── owner_id propagado no registro ────────────────────────────────────────────

def test_owner_id_propagado_no_lancamento(seed):
    svc = ManualEntryService(session_factory=seed["session_factory"], owner_id=42)
    svc.create_transaction(_input(seed))

    # Verifica via query direta que o owner_id foi salvo
    from sqlalchemy import select
    from src.models.db_models import TransactionModel

    with seed["session_factory"]() as session:
        tx = session.scalar(select(TransactionModel))
    assert tx.owner_id == 42


def test_owner_id_none_aceito(seed):
    """Lançamento sem owner_id (usuário anônimo/legado) deve ser salvo normalmente."""
    svc = ManualEntryService(session_factory=seed["session_factory"], owner_id=None)
    svc.create_transaction(_input(seed))

    from sqlalchemy import select
    from src.models.db_models import TransactionModel

    with seed["session_factory"]() as session:
        tx = session.scalar(select(TransactionModel))
    assert tx.owner_id is None
