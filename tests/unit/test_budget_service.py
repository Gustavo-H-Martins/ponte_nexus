"""Testes unitários do BudgetService usando banco SQLite em memória."""
import pandas as pd
import pytest
from decimal import Decimal

from src.services.budget_service import BudgetService
from src.services.catalog_service import CatalogService


@pytest.fixture
def setup(in_memory_session_factory):
    """Retorna (BudgetService, category_id) prontos para uso."""
    catalog = CatalogService(session_factory=in_memory_session_factory)
    cat = catalog.create_category("Alimentação", "pessoal")
    svc = BudgetService(session_factory=in_memory_session_factory)
    return svc, cat.id


def _df_com_despesa(category: str, amount: float, year_month: str) -> pd.DataFrame:
    """DataFrame mínimo compatível com BudgetService.get_utilization()."""
    day = f"{year_month}-01"
    return pd.DataFrame(
        [
            {
                "transaction_type": "despesa",
                "date": pd.Timestamp(day),
                "category": category,
                "amount": amount,
            }
        ]
    )


# ── set_budget / upsert ────────────────────────────────────────────────────────

def test_set_budget_cria_orcamento(setup):
    svc, cat_id = setup
    svc.set_budget(cat_id, "2026-03", Decimal("500"))
    result = svc.get_utilization(pd.DataFrame(), "2026-03")
    assert len(result) == 1
    assert result[0]["limit"] == 500.0


def test_set_budget_atualiza_existente(setup):
    svc, cat_id = setup
    svc.set_budget(cat_id, "2026-03", Decimal("500"))
    svc.set_budget(cat_id, "2026-03", Decimal("800"))
    result = svc.get_utilization(pd.DataFrame(), "2026-03")
    assert result[0]["limit"] == 800.0


def test_set_budget_mes_diferente_nao_interfere(setup):
    svc, cat_id = setup
    svc.set_budget(cat_id, "2026-03", Decimal("500"))
    svc.set_budget(cat_id, "2026-04", Decimal("600"))
    result_mar = svc.get_utilization(pd.DataFrame(), "2026-03")
    result_abr = svc.get_utilization(pd.DataFrame(), "2026-04")
    assert result_mar[0]["limit"] == 500.0
    assert result_abr[0]["limit"] == 600.0


# ── get_utilization ────────────────────────────────────────────────────────────

def test_get_utilization_sem_orcamento_retorna_lista_vazia(setup):
    svc, _ = setup
    result = svc.get_utilization(pd.DataFrame(), "2026-03")
    assert result == []


def test_get_utilization_sem_despesas_spent_zero(setup):
    svc, cat_id = setup
    svc.set_budget(cat_id, "2026-03", Decimal("500"))
    result = svc.get_utilization(pd.DataFrame(), "2026-03")
    assert result[0]["spent"] == 0.0
    assert result[0]["pct"] == 0.0
    assert result[0]["status"] == "ok"


def test_get_utilization_calcula_pct_corretamente(setup):
    svc, cat_id = setup
    svc.set_budget(cat_id, "2026-03", Decimal("400"))
    df = _df_com_despesa("Alimentação", 300.0, "2026-03")
    result = svc.get_utilization(df, "2026-03")
    assert result[0]["pct"] == 75.0
    assert result[0]["status"] == "warning"


def test_get_utilization_status_danger_acima_de_90(setup):
    svc, cat_id = setup
    svc.set_budget(cat_id, "2026-03", Decimal("100"))
    df = _df_com_despesa("Alimentação", 95.0, "2026-03")
    result = svc.get_utilization(df, "2026-03")
    assert result[0]["status"] == "danger"


def test_get_utilization_ignora_despesas_de_outro_mes(setup):
    svc, cat_id = setup
    svc.set_budget(cat_id, "2026-03", Decimal("500"))
    df = _df_com_despesa("Alimentação", 400.0, "2026-04")  # mês diferente
    result = svc.get_utilization(df, "2026-03")
    assert result[0]["spent"] == 0.0


def test_get_utilization_ordena_por_pct_decrescente(in_memory_session_factory):
    catalog = CatalogService(session_factory=in_memory_session_factory)
    cat1 = catalog.create_category("Lazer", "pessoal")
    cat2 = catalog.create_category("Transporte", "pessoal")

    svc = BudgetService(session_factory=in_memory_session_factory)
    svc.set_budget(cat1.id, "2026-03", Decimal("200"))
    svc.set_budget(cat2.id, "2026-03", Decimal("500"))

    df = pd.DataFrame(
        [
            {"transaction_type": "despesa", "date": pd.Timestamp("2026-03-01"), "category": "Lazer",      "amount": 180.0},
            {"transaction_type": "despesa", "date": pd.Timestamp("2026-03-01"), "category": "Transporte", "amount": 100.0},
        ]
    )
    result = svc.get_utilization(df, "2026-03")
    assert result[0]["pct"] >= result[1]["pct"]


# ── Isolamento por owner_id ────────────────────────────────────────────────────

def test_owner_isolamento_orcamentos(in_memory_session_factory):
    catalog = CatalogService(session_factory=in_memory_session_factory)
    cat = catalog.create_category("Moradia", "pessoal")

    svc1 = BudgetService(session_factory=in_memory_session_factory, owner_id=1)
    svc2 = BudgetService(session_factory=in_memory_session_factory, owner_id=2)

    svc1.set_budget(cat.id, "2026-03", Decimal("1000"))

    # owner_id=2 não deve ver o orçamento criado por owner_id=1
    assert svc2.get_utilization(pd.DataFrame(), "2026-03") == []
