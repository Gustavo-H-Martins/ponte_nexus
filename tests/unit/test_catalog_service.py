"""Testes unitários do CatalogService usando banco SQLite em memória."""
from decimal import Decimal

import pytest

from src.services.catalog_service import CatalogService


@pytest.fixture
def catalog(in_memory_session_factory):
    return CatalogService(session_factory=in_memory_session_factory)


# ── Entidades ──────────────────────────────────────────────────────────────────

def test_create_entity_pf(catalog):
    entity = catalog.create_entity("João Silva", "PF")
    assert entity.id is not None
    assert entity.name == "João Silva"
    assert entity.entity_type == "PF"


def test_create_entity_pj(catalog):
    entity = catalog.create_entity("Empresa ABC", "PJ")
    assert entity.entity_type == "PJ"


def test_create_entity_duplicata_levanta_error(catalog):
    catalog.create_entity("João", "PF")
    with pytest.raises(ValueError, match="já existe"):
        catalog.create_entity("João", "PF")


def test_list_entities_retorna_todos(catalog):
    catalog.create_entity("Ana", "PF")
    catalog.create_entity("Beta Ltda", "PJ")
    result = catalog.list_entities()
    assert len(result) == 2


def test_list_entities_filtra_por_tipo(catalog):
    catalog.create_entity("Ana", "PF")
    catalog.create_entity("Beta Ltda", "PJ")
    pf_list = catalog.list_entities(entity_type="PF")
    assert all(e.entity_type == "PF" for e in pf_list)
    assert len(pf_list) == 1


def test_delete_entity(catalog):
    entity = catalog.create_entity("Para Deletar", "PF")
    catalog.delete_entity(entity.id)
    assert catalog.list_entities() == []


# ── Contas ─────────────────────────────────────────────────────────────────────

def test_create_account(catalog):
    entity = catalog.create_entity("Ana", "PF")
    acc = catalog.create_account(
        entity_id=entity.id,
        account_name="Conta Corrente",
        account_type="conta_bancaria",
        currency="BRL",
    )
    assert acc.id is not None
    assert acc.account_name == "Conta Corrente"


def test_create_account_duplicata_levanta_error(catalog):
    entity = catalog.create_entity("Ana", "PF")
    catalog.create_account(entity.id, "CC", "conta_bancaria", "BRL")
    with pytest.raises(ValueError):
        catalog.create_account(entity.id, "CC", "conta_bancaria", "BRL")


def test_list_accounts_with_entity_inclui_balance(catalog):
    entity = catalog.create_entity("Ana", "PF")
    catalog.create_account(entity.id, "CC", "conta_bancaria", "BRL")
    contas = catalog.list_accounts_with_entity()
    assert len(contas) == 1
    assert "balance" in contas[0]
    assert contas[0]["balance"] == Decimal("0")


def test_deactivate_account(catalog):
    entity = catalog.create_entity("Ana", "PF")
    acc = catalog.create_account(entity.id, "CC", "conta_bancaria", "BRL")
    catalog.deactivate_account(acc.id)
    contas = catalog.list_accounts_with_entity()
    assert not contas[0]["is_active"]


# ── Categorias ─────────────────────────────────────────────────────────────────

def test_create_category(catalog):
    cat = catalog.create_category("Alimentação", "pessoal")
    assert cat.name == "Alimentação"
    assert cat.category_group == "pessoal"


def test_create_category_idempotente(catalog):
    cat1 = catalog.create_category("Moradia", "pessoal")
    cat2 = catalog.create_category("Moradia", "pessoal")
    assert cat1.id == cat2.id


def test_delete_category(catalog):
    cat = catalog.create_category("Transporte", "pessoal")
    catalog.delete_category(cat.id)
    assert catalog.list_categories() == []


# ── Empresas ───────────────────────────────────────────────────────────────────

def test_create_company(catalog):
    companies = catalog.create_company("Tech Ltda", "12.345.678/0001-90", "ltda")
    assert companies.cnpj == "12345678000190"


def test_create_company_cnpj_invalido_levanta_error(catalog):
    with pytest.raises(ValueError, match="14 dígitos"):
        catalog.create_company("Tech", "123", "ltda")


def test_create_company_cnpj_duplicado_levanta_error(catalog):
    catalog.create_company("Tech A", "12.345.678/0001-90", "ltda")
    with pytest.raises(ValueError, match="já cadastrada"):
        catalog.create_company("Tech B", "12.345.678/0001-90", "ltda")


def test_list_companies(catalog):
    catalog.create_company("Tech Ltda", "12.345.678/0001-90", "ltda")
    result = catalog.list_companies()
    assert len(result) == 1
    assert result[0]["nome_empresa"] == "Tech Ltda"


# ── Isolamento por owner_id ────────────────────────────────────────────────────

def test_owner_isolamento_entidades(in_memory_session_factory):
    svc1 = CatalogService(session_factory=in_memory_session_factory, owner_id=1)
    svc2 = CatalogService(session_factory=in_memory_session_factory, owner_id=2)

    svc1.create_entity("Pertence ao user 1", "PF")
    assert svc2.list_entities() == []
    assert len(svc1.list_entities()) == 1
