import pytest

from src.domain.enums import EntityType, TransactionType
from src.domain.rules import validate_flow_direction


# ── Fluxos PF → PJ ───────────────────────────────────────────────────────────


def test_aporte_pf_pj_valido() -> None:
    validate_flow_direction(TransactionType.APORTE_PF_PJ, EntityType.PF, EntityType.PJ)


def test_emprestimo_pf_pj_valido() -> None:
    validate_flow_direction(TransactionType.EMPRESTIMO_PF_PJ, EntityType.PF, EntityType.PJ)


def test_transferencia_pf_pj_valido() -> None:
    validate_flow_direction(TransactionType.TRANSFERENCIA_PF_PJ, EntityType.PF, EntityType.PJ)


def test_aporte_invertido_levanta_excecao() -> None:
    with pytest.raises(ValueError, match="PF -> PJ"):
        validate_flow_direction(TransactionType.APORTE_PF_PJ, EntityType.PJ, EntityType.PF)


def test_emprestimo_origem_errada_levanta_excecao() -> None:
    with pytest.raises(ValueError, match="PF -> PJ"):
        validate_flow_direction(TransactionType.EMPRESTIMO_PF_PJ, EntityType.PJ, EntityType.PJ)


# ── Fluxos PJ → PF ───────────────────────────────────────────────────────────


def test_dividendos_pj_pf_valido() -> None:
    validate_flow_direction(TransactionType.DIVIDENDOS, EntityType.PJ, EntityType.PF)


def test_pro_labore_pj_pf_valido() -> None:
    validate_flow_direction(TransactionType.PRO_LABORE, EntityType.PJ, EntityType.PF)


def test_transferencia_pj_pf_valido() -> None:
    validate_flow_direction(TransactionType.TRANSFERENCIA_PJ_PF, EntityType.PJ, EntityType.PF)


def test_dividendos_invertido_levanta_excecao() -> None:
    with pytest.raises(ValueError, match="PJ -> PF"):
        validate_flow_direction(TransactionType.DIVIDENDOS, EntityType.PF, EntityType.PJ)


def test_pro_labore_origem_errada_levanta_excecao() -> None:
    with pytest.raises(ValueError, match="PJ -> PF"):
        validate_flow_direction(TransactionType.PRO_LABORE, EntityType.PF, EntityType.PF)


# ── Tipos neutros (sem restrição de direção) ──────────────────────────────────


def test_receita_nao_valida_direcao_pj_pj() -> None:
    """Tipos neutros como 'receita' não devem levantar exceção em nenhuma combinação."""
    validate_flow_direction(TransactionType.RECEITA, EntityType.PJ, EntityType.PJ)


def test_despesa_nao_valida_direcao_pf_pf() -> None:
    validate_flow_direction(TransactionType.DESPESA, EntityType.PF, EntityType.PF)
