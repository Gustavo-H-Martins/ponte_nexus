import pandas as pd

from src.validation.validators import validate_dataframe

_VALID_ROW = {
    "id_lancamento": "tx-001",
    "data": "2026-01-05",
    "tipo_entidade": "PJ",
    "nome_entidade": "Empresa X",
    "tipo_transacao": "receita",
    "categoria": "vendas",
    "descricao": "Recebimento",
    "valor": "15000.00",
    "moeda": "BRL",
    "conta_origem": "Conta Empresa",
    "conta_destino": "Conta Empresa",
}


def test_missing_columns_returns_error():
    df = pd.DataFrame([{"foo": 1}])
    errors = validate_dataframe(df)
    assert errors
    assert errors[0]["error_code"] == "missing_columns"


def test_valid_dataframe_returns_no_errors():
    df = pd.DataFrame([_VALID_ROW])
    errors = validate_dataframe(df)
    assert errors == []


def test_invalid_amount_returns_error():
    df = pd.DataFrame([{**_VALID_ROW, "valor": "-100.00"}])
    errors = validate_dataframe(df)
    assert any(e.get("field_name") == "valor" for e in errors)


def test_invalid_entity_type_returns_error():
    df = pd.DataFrame([{**_VALID_ROW, "tipo_entidade": "SA"}])
    errors = validate_dataframe(df)
    assert errors
