import pandas as pd
import pytest

from src.analytics.kpis import (
    income_by_source,
    income_expense_summary,
    monthly_net_result,
    period_comparison,
    pf_pj_kpis,
    top_expense_categories,
)

_BASE_ROWS = [
    {"date": "2026-01-10", "transaction_type": "receita",  "amount": 10000.0, "category": "vendas"},
    {"date": "2026-01-15", "transaction_type": "despesa",  "amount": 3000.0,  "category": "aluguel"},
    {"date": "2026-01-20", "transaction_type": "despesa",  "amount": 1500.0,  "category": "software"},
    {"date": "2026-01-25", "transaction_type": "pro_labore", "amount": 4000.0, "category": "pro_labore"},
    {"date": "2026-01-28", "transaction_type": "dividendos", "amount": 2000.0, "category": "dividendos"},
    {"date": "2026-02-10", "transaction_type": "receita",  "amount": 12000.0, "category": "vendas"},
    {"date": "2026-02-18", "transaction_type": "despesa",  "amount": 3500.0,  "category": "aluguel"},
]


@pytest.fixture()
def df() -> pd.DataFrame:
    return pd.DataFrame(_BASE_ROWS)


# ── income_expense_summary ────────────────────────────────────────────────────


def test_income_expense_summary_vazios() -> None:
    result = income_expense_summary(pd.DataFrame())
    assert result == {"income": 0.0, "expense": 0.0, "net": 0.0}


def test_income_expense_summary_calcula_corretamente(df: pd.DataFrame) -> None:
    result = income_expense_summary(df)
    assert result["income"] == pytest.approx(22000.0)
    assert result["expense"] == pytest.approx(8000.0)
    assert result["net"] == pytest.approx(14000.0)


# ── pf_pj_kpis ───────────────────────────────────────────────────────────────


def test_pf_pj_kpis_vazios() -> None:
    result = pf_pj_kpis(pd.DataFrame())
    assert result["pj_income"] == 0.0
    assert result["pf_income"] == 0.0


def test_pf_pj_kpis_calcula_pf_income(df: pd.DataFrame) -> None:
    result = pf_pj_kpis(df)
    assert result["pf_income"] == pytest.approx(6000.0)  # pro_labore + dividendos
    assert result["pj_income"] == pytest.approx(22000.0)


# ── monthly_net_result ────────────────────────────────────────────────────────


def test_monthly_net_result_vazio() -> None:
    empty = pd.DataFrame(columns=["date", "transaction_type", "amount"])
    result = monthly_net_result(empty)
    assert list(result.columns) == ["month", "signed_amount"]
    assert result.empty


def test_monthly_net_result_dois_meses(df: pd.DataFrame) -> None:
    result = monthly_net_result(df)
    assert len(result) == 2
    jan = result[result["month"] == "2026-01"]["signed_amount"].iloc[0]
    assert jan == pytest.approx(5500.0)  # 10000 - 3000 - 1500


# ── income_by_source ──────────────────────────────────────────────────────────


def test_income_by_source_vazio() -> None:
    result = income_by_source(pd.DataFrame(columns=["transaction_type", "amount", "category"]))
    assert result.empty


def test_income_by_source_retorna_ordenado(df: pd.DataFrame) -> None:
    result = income_by_source(df)
    # Primeira linha deve ter o maior valor
    assert result.iloc[0]["amount"] >= result.iloc[1]["amount"]


# ── top_expense_categories ────────────────────────────────────────────────────


def test_top_expense_categories_vazio() -> None:
    result = top_expense_categories(pd.DataFrame(columns=["transaction_type", "amount", "category"]))
    assert result.empty


def test_top_expense_categories_limita_n(df: pd.DataFrame) -> None:
    result = top_expense_categories(df, n=1)
    assert len(result) == 1
    assert result.iloc[0]["category"] == "aluguel"  # maior despesa


# ── period_comparison ─────────────────────────────────────────────────────────


def test_period_comparison_retorna_chaves_esperadas(df: pd.DataFrame) -> None:
    result = period_comparison(df, "2026-02", "2026-01")
    expected_keys = {
        "income_current", "income_previous", "income_delta_pct",
        "expense_current", "expense_previous", "expense_delta_pct",
        "net_current", "net_previous", "net_delta_pct",
    }
    assert set(result.keys()) == expected_keys


def test_period_comparison_delta_positivo(df: pd.DataFrame) -> None:
    result = period_comparison(df, "2026-02", "2026-01")
    # Receita de fev (12000) > jan (10000) → delta positivo
    assert result["income_delta_pct"] > 0


def test_period_comparison_periodo_sem_dados_retorna_zero(df: pd.DataFrame) -> None:
    result = period_comparison(df, "2026-03", "2026-01")
    assert result["income_current"] == 0.0
    assert result["income_delta_pct"] == pytest.approx(-100.0)
